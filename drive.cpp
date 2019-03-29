#include <algorithm>
#include <cmath>
#include <vector>
#include <string>
#include <sstream>
#include <unordered_map>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

using namespace std;

static vector<string> strsplit(const string &text, char sep) {
  vector<string> tokens;
  size_t start = 0, end = 0;
  while ((end = text.find(sep, start)) != string::npos) {
    tokens.push_back(text.substr(start, end - start));
    start = end + 1;
  }
  tokens.push_back(text.substr(start));
  return tokens;
}

struct Point { double x,y; };

Point subtract(Point p1, Point p2) { return { p1.x - p2.x, p1.y - p2.y }; }
double inner_product(Point p1, Point p2) { return p1.x * p2.x + p1.y * p2.y; }
double norm2(Point p) { return inner_product(p,p); }

Point to_meters(double lat, double lon) {
  // Approximations:
  // earth radius ~ 6400km
  // israel lat ~ 32 degrees
  // cos(32 degrees) ~ 0.84

  return { (lat - 32) / 180 * 3.141592653589 * 6400000,
           (lon - 34) / 180 * 3.141592653589 * 6400000 * 0.84 };
}

Point create_point(const string& lat, const string& lon) {
  return to_meters(atof(lat.c_str()),atof(lon.c_str()));
}

struct Interval {
  Point a, b;
  Point ba;
  double ba_2;
};

struct Shape {
  string shape_id;
  string route_id;
  vector<Point> points;

  vector<Point> interval_diff;
  vector<double> interval_norm2;
  Interval get_interval(int i) const {
    return Interval{ points[i], points[i+1], interval_diff[i], interval_norm2[i] };
  }
  int size() const { return points.size() - 1; }
  void prepare() {
    interval_diff.reserve(size());
    interval_norm2.reserve(size());
    for (int i = 0; i < size(); i++) {
      interval_diff.push_back(subtract(points[i+1], points[i]));
      interval_norm2.push_back(norm2(interval_diff[i]));
    }
  }

  double last_distance_calc;
};

double interval_distance(Interval inter, Point x) {
  Point da = subtract(x, inter.a);
  double t = inner_product(da, inter.ba);
  double ret;
  if (t <= 0) {
    ret = norm2(da);
  } else if (t >= inter.ba_2) {
    Point db = subtract(x, inter.b);
    ret = norm2(db);
  } else {
    ret = norm2(da) - t*t / inter.ba_2;
  }
  //printf("%g - %g %g, %g %g, %g %g\n", ret, inter.a.x, inter.a.y, inter.b.x, inter.b.y, x.x, x.y);
  return ret;
}

double shape_distance(const Shape& shape, Point x) {
  double min = interval_distance(shape.get_interval(0), x);
  for (int i = 1; i < shape.size(); i++) {
    double tmp = interval_distance(shape.get_interval(i), x);
    if (tmp < min) min = tmp;
  }
  return min;
}

struct Drive {
  string trip_id;
  string route_id;
  vector<Point> points;
};

double drive_distance(const Shape& shape, const Drive& drive) {
  double sum = 0;
  shape_distance(shape, drive.points[1]);
  for (Point p : drive.points) sum += shape_distance(shape, p);
  //for (Point p : drive.points) printf("%g\n", shape_distance(shape, p));
  return sqrt(sum / drive.points.size());
}

vector<Shape> read_shapes(const char *filename) {
  vector<Shape> ret;
  ostringstream line;
  int c, first = 1;
  FILE* txtfile = fopen(filename, "rb");
  Shape cur = {};
  while ((c = fgetc(txtfile)) != EOF) {
    if (c != '\n') { line << (char)c; continue; }
    vector<string> tmp = strsplit(line.str(), ',');
    line.str("");
    if (tmp.size() < 2) continue;
    if (first) { first = 0; continue; }

    const string& shape_id = tmp[0];
    const string& route_id = tmp[4];
    const string& lat = tmp[1];
    const string& lon = tmp[2];
    if (cur.shape_id != shape_id) {
      if (cur.points.size() > 1) ret.push_back(move(cur));
      cur.shape_id = shape_id;
      cur.route_id = route_id;
      cur.points.clear();
    }
    cur.points.push_back(create_point(lat, lon));
  }
  if (cur.points.size() > 1) ret.push_back(move(cur));
  for (auto& shape : ret) shape.prepare();
  fclose(txtfile);
  return ret;
}

vector<Drive> read_drives(const char *filename) {
  vector<Drive> ret;
  ostringstream line;
  int c, first = 1;
  FILE* txtfile = fopen(filename, "rb");
  Drive cur = {};
  while ((c = fgetc(txtfile)) != EOF) {
    if (c != '\n') { line << (char)c; continue; }
    vector<string> tmp = strsplit(line.str(), ',');
    line.str("");
    if (tmp.size() < 2) continue;
    if (first) { first = 0; continue; }

    const string& trip_id = tmp[0];
    const string& route_id = tmp[5];
    const string& lat = tmp[3];
    const string& lon = tmp[4];
    if (cur.trip_id != trip_id) {
      if (cur.points.size()) ret.push_back(move(cur));
      cur.trip_id = trip_id;
      cur.route_id = route_id;
      cur.points.clear();
    }
    cur.points.push_back(create_point(lat, lon));
  }
  if (cur.points.size()) ret.push_back(move(cur));
  fclose(txtfile);
  return ret;
}

int main() {
  auto shapes = read_shapes("data/shapes.csv");
  auto drives = read_drives("data/train.csv");

  struct Res { Shape *pshape; double distance; };
  vector<Res> res;
  res.reserve(shapes.size());

  //printf("trip_id,distance,certainty,shape_id,route_id,num_points,mismatch_route_id\n");
  printf("trip_id,distance,rid\n");

  size_t N = drives.size();
  //N = 20;
  for (size_t d = 0; d < N; d++) {
    res.clear();

    auto& drive = drives[d];
    if (drive.points.size() < 20) continue;

    //printf("%s\n", drive.trip_id.c_str());

    for (auto& shape : shapes) res.push_back({ &shape, drive_distance(shape, drive) });

    sort(res.begin(), res.end(), [](Res&a, Res&b){ return a.distance < b.distance; });

#if 0
    auto& r = res[0];
    Res *r2 = nullptr;
    for (int i = 1; i < res.size(); i++) {
      if (res[i].pshape->route_id != r.pshape->route_id) { r2 = &res[i]; break; }
    }
    double certainty = (r2 ? (1. - r.distance / r2->distance) : 0);
    printf("%s,%g,%g,%s,%s,%d", drive.trip_id.c_str(), r.distance, certainty, r.pshape->shape_id.c_str(), r.pshape->route_id.c_str(), int(drive.points.size()));
    if (drive.route_id != r.pshape->route_id) printf(",MISMATCH-%s", drive.route_id.c_str());
    printf("\n");
#else
    for (auto& r : res) {
      printf("%s %s,%g,%s %s\n", drive.trip_id.c_str(), drive.route_id.c_str(), r.distance, r.pshape->shape_id.c_str(), r.pshape->route_id.c_str());
    }
#endif
  }
  return 0;
}
