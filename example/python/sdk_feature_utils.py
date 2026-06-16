"""SdkFeature bitmask helpers (works with all pybind builds)."""

from __future__ import annotations

import magicdog_python as magicdog


def combine_sdk_features(*features: magicdog.SdkFeature) -> magicdog.SdkFeature:
    if not features:
        return magicdog.SdkFeature.NONE
    acc = features[0]
    for feat in features[1:]:
        try:
            acc = acc | feat
        except TypeError:
            acc = magicdog.SdkFeature(int(acc) | int(feat))
    return acc


def motion_and_slam_features() -> magicdog.SdkFeature:
    return combine_sdk_features(
        magicdog.SdkFeature.HIGH_LEVEL_MOTION,
        magicdog.SdkFeature.SLAM_NAVIGATION,
    )
