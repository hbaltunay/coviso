#pragma once
#include <cstdint>
#include <random>
#include <utility>
#include <vector>

inline constexpr double kPi = 3.14159265358979323846;

class Rng {
 public:
  Rng(uint64_t master, uint64_t stream);

  double u01();                                   // [0, 1)
  double uniform(double a, double b);             // [a, b)
  int uniformInt(int a, int b);                   // [a, b]
  bool bernoulli(double p);

  double normal(double mean, double sd);          // Box-Muller
  double truncNormal(double mean, double sd, double lo, double hi);
  double logNormal(double median, double sigma);

  template <class T>
  void shuffle(std::vector<T>& v) {               // Fisher-Yates
    for (size_t i = v.size(); i > 1; --i)
      std::swap(v[i - 1], v[size_t(uniformInt(0, int(i) - 1))]);
  }

 private:
  static uint64_t splitmix(uint64_t z);
  std::mt19937_64 eng_;
};