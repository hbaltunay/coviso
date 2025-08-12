from collections import defaultdict
from typing import Any

import numpy as np
from torch import Tensor

from ..utils.ops import xyxy2xywh


def untracked_result(result: Tensor) -> dict[str, Any]:
    res = {}
    res["xyxy"] = result[:, :4].numpy().astype(np.int32)
    res["conf"] = result[:, 4].numpy()
    res["cls"] = result[:, 5].numpy().astype(np.int32)

    return res


def tracked_result(result: Tensor) -> dict[str, Any]:
    res = defaultdict(dict)
    track_ids = [str(tid) for tid in result[:, 4].numpy().astype(np.int32)]

    for i, tid in enumerate(track_ids):
        res[tid]["xyxy"] = result[i, :4].numpy().astype(np.int32)
        res[tid]["xywh"] = xyxy2xywh(res[tid]["xyxy"]).astype(np.int32)
        res[tid]["center"] = res[tid]["xywh"][:2]
        res[tid]["tid"] = result[i, 4].numpy().astype(np.int32)
        res[tid]["conf"] = result[i, 5].numpy()
        res[tid]["cls"] = result[i, 6].numpy().astype(np.int32)

    return dict(res)
