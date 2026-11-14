#include "cv/solution/entity.hpp"
#include "cv/tool/logger.hpp"

// =============================================================================
// Entity Zone
// =============================================================================

EntityZone::EntityZone(int zoneCtrl) : zoneCtrl_(zoneCtrl) {}

void EntityZone::add(int tid, int location) {
    entities[tid] = EntityZ{tid, 0, location, Status::ACTIVE, location, location, SteadyClock::now()};
}

void EntityZone::update(int tid, int location) {
    if (!appliedIds.count(tid)) {
        add(tid, location);
        appliedIds.emplace(tid);
    } else {
        entities[tid].currentLocation = location;
        entities[tid].status = Status::ACTIVE;
    }
}

void EntityZone::apply() {
    for (auto& [tid, entity] : entities) {
        if (!check(entity)) continue;

        if (entity.lastLocation != entity.currentLocation) {
            entity.ctrl = 0;
        }

        if (entity.location != entity.currentLocation) {
            if (entity.ctrl > zoneCtrl_) {
                entity.exitTime = SteadyClock::now();
                log(entity);
                entity.location = entity.currentLocation;
                entity.entryTime = SteadyClock::now();
                entity.exitTime = {};
                entity.ctrl = 0;
            } else {
                entity.ctrl++;
            }
        }

        entity.lastLocation = entity.currentLocation;
        entity.status = Status::APPLIED;
    }
}

void EntityZone::log(EntityZ entity) {
    LOG_INFO("Track Id: {} | Location: {}", entity.tid, entity.location);
}

// =============================================================================
// Entity Line
// =============================================================================

EntityLine::EntityLine() {}

void EntityLine::add(int tid, int location) {
    entities[tid] = EntityL{tid, 0, location, Status::ACTIVE};
}

void EntityLine::update(int tid, int location) {
    if (!appliedIds.count(tid)) {
        add(tid, location);
        appliedIds.emplace(tid);
    } else {
        entities[tid].location = location;
        entities[tid].status = Status::ACTIVE;
    }
}

void EntityLine::onPassed(int tid, int location) {
    entities[tid].passedLocation = location;
    entities[tid].passedTime = SteadyClock::now();
    entities[tid].passed = true;
}

void EntityLine::apply() {
    for (auto& [tid, entity] : entities) {
        if (!check(entity)) continue;

        if (entity.passed) {
            log(entity);
            entity.passed = false;
        }

        entity.status = Status::APPLIED;
    }
}

void EntityLine::log(EntityL entity) {
    LOG_INFO("Track Id: {} | Passed Line: {}", entity.tid, entity.passedLocation);
}