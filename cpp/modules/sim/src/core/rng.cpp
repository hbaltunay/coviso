#include <algorithm>
#include <cmath>

#include "cv/sim/core/rng.hpp"


Rng::Rng(uint64_t master, uint64_t stream)
    : eng_(splitmix(master ^ splitmix(stream))) {}

double Rng::u01() {
  return double(eng_() >> 11) * (1.0 / 9007199254740992.0);
}

double Rng::uniform(double a, double b) { return a + (b - a) * u01(); }

int Rng::uniformInt(int a, int b) {
  return std::min(b, a + int(u01() * (b - a + 1)));
}

bool Rng::bernoulli(double p) { return u01() < p; }

double Rng::normal(double mean, double sd) {
  double u1 = std::max(u01(), 1e-300), u2 = u01();
  return mean + sd * std::sqrt(-2.0 * std::log(u1)) * std::cos(2.0 * kPi * u2);
}

double Rng::truncNormal(double mean, double sd, double lo, double hi) {
  for (int i = 0; i < 32; ++i) {
    double x = normal(mean, sd);
    if (x >= lo && x <= hi) return x;
  }
  return std::clamp(mean, lo, hi);
}

double Rng::logNormal(double median, double sigma) {
  return median * std::exp(normal(0.0, sigma));
}

uint64_t Rng::splitmix(uint64_t z) {
  z += 0x9E3779B97F4A7C15ULL;
  z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
  z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
  return z ^ (z >> 31);
}