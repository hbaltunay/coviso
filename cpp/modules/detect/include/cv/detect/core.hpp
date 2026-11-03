#pragma once


struct BBox { int x, y, w, h; };
  
struct Detection {
    BBox bbox;
    int classId;
    int trackId;
};
