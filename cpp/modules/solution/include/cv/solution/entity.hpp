#pragma once

#include <chrono>
#include <unordered_set>
#include <unordered_map>

using SteadyClock = std::chrono::steady_clock;
using SysClock    = std::chrono::system_clock;

static const auto steady0 = SteadyClock::now();
static const auto sys0    = SysClock::now();

enum class Status {
    APPLIED = 0,
    ACTIVE = 1,
    LOST = 2,
    REMOVE = 3
};

struct EntityB {
    int tid;
    int exist = 0;
    int location = 0;
    Status status = Status::ACTIVE;
};

template <typename T>
class EntityBase {
protected:
    int existNum = 90;
    std::unordered_set<int> appliedIds;
    std::unordered_map<int, T> entities;

    bool check(T entity);
};

template <typename T>
bool EntityBase<T>::check(T entity) {
    if (entity.status == Status::ACTIVE) {
        entity.exist = 0;
        return true;
    }

    entity.status = Status::LOST;

    if (entity.exist > this->existNum) {
        entity.status = Status::REMOVE;
        this->entities.erase(entity.tid);
        this->appliedIds.erase(entity.tid);
    }

    entity.exist++;

    return false;
}

struct EntityZ : public EntityB {
    int currentLocation = 0;
    int lastLocation = 0;
    SteadyClock::time_point entryTime{};
    SteadyClock::time_point exitTime{};
    int ctrl = 0;
};

class EntityZone : public EntityBase<EntityZ> {
private:
    int zoneCtrl_ = 90;
    void add(int tid, int location);
    void log(EntityZ entity);

public:
    EntityZone(int zoneCtrl = 90);
    void apply();
    void update(int tid, int location);
};

struct EntityL : public EntityB {
    int passedLocation = 0;
    SteadyClock::time_point passedTime{};
    bool passed = false;
};

class EntityLine : public EntityBase<EntityL> {
private:
    void add(int tid, int location);
    void log(EntityL entity);

public:
    EntityLine();
    void update(int tid, int location);
    void onPassed(int tid, int location);
    void apply();
};