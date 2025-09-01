"""
MagicDog SDK Python Binding Module
"""
from __future__ import annotations
import collections.abc
import typing
__all__: list[str] = ['AudioController', 'BatteryState', 'BmsData', 'BotConfig', 'BotConfigSelected', 'BotInfo', 'ByteMultiArray', 'CameraInfo', 'CompressedImage', 'ControllerLevel', 'CustomBotInfo', 'DialogConfig', 'Double12Array', 'Double3Array', 'Double4Array', 'Double9Array', 'DoubleVector', 'ErrorCode', 'Fault', 'FaultVector', 'Float32MultiArray', 'FloatVector', 'GaitMode', 'GetSpeechConfig', 'Header', 'HighLevelMotionController', 'Image', 'Imu', 'Int8', 'JoystickCommand', 'LEG_JOINT_NUM', 'LaserScan', 'LegJointCommand', 'LegJointCommandArray', 'LegJointStateArray', 'LegState', 'LowLevelMotionController', 'MagicRobot', 'MultiArrayDimension', 'MultiArrayDimensionVector', 'MultiArrayLayout', 'PERIOD_MS', 'PointCloud2', 'PointField', 'PointFieldVector', 'PowerSupplyStatus', 'RobotState', 'S2DString', 'S2DStringVector', 'SensorController', 'SetSpeechConfig', 'SingleLegJointCommand', 'SingleLegJointState', 'SpeakerConfig', 'SpeakerConfigSelected', 'StateMonitor', 'Status', 'String2DStringVectorMap', 'StringBotConfigMap', 'StringBotInfoMap', 'StringCustomBotMap', 'StringStringMap', 'TrickAction', 'TrinocularCameraFrame', 'TtsCommand', 'TtsMode', 'TtsPriority', 'TtsType', 'Uint8Vector', 'WakeupConfig']
class AudioController:
    def __init__(self) -> None:
        ...
    def control_voice_stream(self, arg0: bool, arg1: bool) -> Status:
        ...
    def get_voice_config(self) -> GetSpeechConfig:
        """
        Get voice configuration, returns config object on success, empty config on failure
        """
    def get_volume(self) -> int:
        """
        Get current volume, returns volume value on success, -1 on failure
        """
    def initialize(self) -> bool:
        ...
    def play(self, arg0: TtsCommand) -> Status:
        ...
    def set_voice_config(self, arg0: SetSpeechConfig) -> Status:
        ...
    def set_volume(self, arg0: typing.SupportsInt) -> Status:
        ...
    def shutdown(self) -> None:
        ...
    def stop(self) -> Status:
        ...
    def subscribe_bf_voice_data(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to BF voice data
        """
    def subscribe_origin_voice_data(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to original voice data
        """
    def switch_tts_voice_model(self, arg0: TtsType, arg1: GetSpeechConfig) -> Status:
        """
        Switch TTS voice model
        """
class BatteryState:
    """
    Members:
    
      UNKNOWN
    
      GOOD
    
      OVERHEAT
    
      DEAD
    
      OVERVOLTAGE
    
      UNSPEC_FAILURE
    
      COLD
    
      WATCHDOG_TIMER_EXPIRE
    
      SAFETY_TIMER_EXPIRE
    """
    COLD: typing.ClassVar[BatteryState]  # value = <BatteryState.COLD: 6>
    DEAD: typing.ClassVar[BatteryState]  # value = <BatteryState.DEAD: 3>
    GOOD: typing.ClassVar[BatteryState]  # value = <BatteryState.GOOD: 1>
    OVERHEAT: typing.ClassVar[BatteryState]  # value = <BatteryState.OVERHEAT: 2>
    OVERVOLTAGE: typing.ClassVar[BatteryState]  # value = <BatteryState.OVERVOLTAGE: 4>
    SAFETY_TIMER_EXPIRE: typing.ClassVar[BatteryState]  # value = <BatteryState.SAFETY_TIMER_EXPIRE: 8>
    UNKNOWN: typing.ClassVar[BatteryState]  # value = <BatteryState.UNKNOWN: 0>
    UNSPEC_FAILURE: typing.ClassVar[BatteryState]  # value = <BatteryState.UNSPEC_FAILURE: 5>
    WATCHDOG_TIMER_EXPIRE: typing.ClassVar[BatteryState]  # value = <BatteryState.WATCHDOG_TIMER_EXPIRE: 7>
    __members__: typing.ClassVar[dict[str, BatteryState]]  # value = {'UNKNOWN': <BatteryState.UNKNOWN: 0>, 'GOOD': <BatteryState.GOOD: 1>, 'OVERHEAT': <BatteryState.OVERHEAT: 2>, 'DEAD': <BatteryState.DEAD: 3>, 'OVERVOLTAGE': <BatteryState.OVERVOLTAGE: 4>, 'UNSPEC_FAILURE': <BatteryState.UNSPEC_FAILURE: 5>, 'COLD': <BatteryState.COLD: 6>, 'WATCHDOG_TIMER_EXPIRE': <BatteryState.WATCHDOG_TIMER_EXPIRE: 7>, 'SAFETY_TIMER_EXPIRE': <BatteryState.SAFETY_TIMER_EXPIRE: 8>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class BmsData:
    battery_state: BatteryState
    power_supply_status: PowerSupplyStatus
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def battery_health(self) -> float:
        ...
    @battery_health.setter
    def battery_health(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def battery_percentage(self) -> float:
        ...
    @battery_percentage.setter
    def battery_percentage(self, arg0: typing.SupportsFloat) -> None:
        ...
class BotConfig:
    custom_data: StringCustomBotMap
    data: StringBotInfoMap
    selected: BotConfigSelected
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class BotConfigSelected:
    bot_id: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class BotInfo:
    name: str
    workflow: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class ByteMultiArray:
    data: Uint8Vector
    layout: MultiArrayLayout
    def __copy__(self) -> ByteMultiArray:
        ...
    def __deepcopy__(self, arg0: dict) -> ByteMultiArray:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get byte array length
        """
    def __repr__(self) -> str:
        ...
class CameraInfo:
    D: DoubleVector
    K: Double9Array
    P: Double12Array
    R: Double9Array
    distortion_model: str
    header: Header
    roi_do_rectify: bool
    def __copy__(self) -> CameraInfo:
        ...
    def __deepcopy__(self, arg0: dict) -> CameraInfo:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get distortion parameter array length
        """
    def __repr__(self) -> str:
        ...
    @property
    def binning_x(self) -> int:
        ...
    @binning_x.setter
    def binning_x(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def binning_y(self) -> int:
        ...
    @binning_y.setter
    def binning_y(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def height(self) -> int:
        ...
    @height.setter
    def height(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def roi_height(self) -> int:
        ...
    @roi_height.setter
    def roi_height(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def roi_width(self) -> int:
        ...
    @roi_width.setter
    def roi_width(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def roi_x_offset(self) -> int:
        ...
    @roi_x_offset.setter
    def roi_x_offset(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def roi_y_offset(self) -> int:
        ...
    @roi_y_offset.setter
    def roi_y_offset(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def width(self) -> int:
        ...
    @width.setter
    def width(self, arg0: typing.SupportsInt) -> None:
        ...
class CompressedImage:
    data: Uint8Vector
    format: str
    header: Header
    def __copy__(self) -> CompressedImage:
        ...
    def __deepcopy__(self, arg0: dict) -> CompressedImage:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get compressed image data byte count
        """
    def __repr__(self) -> str:
        ...
class ControllerLevel:
    """
    Members:
    
      UNKNOWN
    
      HIGH_LEVEL
    
      LOW_LEVEL
    """
    HIGH_LEVEL: typing.ClassVar[ControllerLevel]  # value = <ControllerLevel.HIGH_LEVEL: 1>
    LOW_LEVEL: typing.ClassVar[ControllerLevel]  # value = <ControllerLevel.LOW_LEVEL: 2>
    UNKNOWN: typing.ClassVar[ControllerLevel]  # value = <ControllerLevel.UNKNOWN: 0>
    __members__: typing.ClassVar[dict[str, ControllerLevel]]  # value = {'UNKNOWN': <ControllerLevel.UNKNOWN: 0>, 'HIGH_LEVEL': <ControllerLevel.HIGH_LEVEL: 1>, 'LOW_LEVEL': <ControllerLevel.LOW_LEVEL: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class CustomBotInfo:
    name: str
    token: str
    workflow: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class DialogConfig:
    is_doa_enable: bool
    is_enable: bool
    is_front_doa: bool
    is_fullduplex_enable: bool
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class Double12Array:
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
class Double3Array:
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
class Double4Array:
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
class Double9Array:
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
class DoubleVector:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: typing.SupportsFloat) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: DoubleVector) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> DoubleVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: DoubleVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: DoubleVector) -> bool:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: DoubleVector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: typing.SupportsFloat) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: typing.SupportsFloat) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: DoubleVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: typing.SupportsFloat) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> float:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> float:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: typing.SupportsFloat) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class ErrorCode:
    """
    Members:
    
      OK
    
      SERVICE_NOT_READY
    
      TIMEOUT
    
      INTERNAL_ERROR
    
      SERVICE_ERROR
    """
    INTERNAL_ERROR: typing.ClassVar[ErrorCode]  # value = <ErrorCode.INTERNAL_ERROR: 3>
    OK: typing.ClassVar[ErrorCode]  # value = <ErrorCode.OK: 0>
    SERVICE_ERROR: typing.ClassVar[ErrorCode]  # value = <ErrorCode.SERVICE_ERROR: 4>
    SERVICE_NOT_READY: typing.ClassVar[ErrorCode]  # value = <ErrorCode.SERVICE_NOT_READY: 1>
    TIMEOUT: typing.ClassVar[ErrorCode]  # value = <ErrorCode.TIMEOUT: 2>
    __members__: typing.ClassVar[dict[str, ErrorCode]]  # value = {'OK': <ErrorCode.OK: 0>, 'SERVICE_NOT_READY': <ErrorCode.SERVICE_NOT_READY: 1>, 'TIMEOUT': <ErrorCode.TIMEOUT: 2>, 'INTERNAL_ERROR': <ErrorCode.INTERNAL_ERROR: 3>, 'SERVICE_ERROR': <ErrorCode.SERVICE_ERROR: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Fault:
    error_message: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def error_code(self) -> int:
        ...
    @error_code.setter
    def error_code(self, arg0: typing.SupportsInt) -> None:
        ...
class FaultVector:
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> FaultVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: FaultVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ...) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: FaultVector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: ...) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: FaultVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: ...) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ...:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> ...:
        """
        Remove and return the item at index ``i``
        """
class Float32MultiArray:
    data: FloatVector
    layout: MultiArrayLayout
    def __copy__(self) -> Float32MultiArray:
        ...
    def __deepcopy__(self, arg0: dict) -> Float32MultiArray:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get float array length
        """
    def __repr__(self) -> str:
        ...
class FloatVector:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: typing.SupportsFloat) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: FloatVector) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> FloatVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> float:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: FloatVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: FloatVector) -> bool:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsFloat) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: FloatVector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: typing.SupportsFloat) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: typing.SupportsFloat) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: FloatVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: typing.SupportsFloat) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> float:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> float:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: typing.SupportsFloat) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class GaitMode:
    """
    Members:
    
      GAIT_PASSIVE
    
      GAIT_STAND_R
    
      GAIT_STAND_B
    
      GAIT_RUN_FAST
    
      GAIT_DOWN_CLIMB_STAIRS
    
      GAIT_TROT
    
      GAIT_PRONK
    
      GAIT_BOUND
    
      GAIT_AMBLE
    
      GAIT_CRAWL
    
      GAIT_LOWLEVL_SDK
    
      GAIT_WALK
    
      GAIT_UP_CLIMB_STAIRS
    
      GAIT_RL_TERRAIN
    
      GAIT_RL_FALL_RECOVERY
    
      GAIT_RL_HAND_STAND
    
      GAIT_RL_FOOT_STAND
    
      GAIT_ENTER_RL
    
      GAIT_DEFAULT
    
      GAIT_NONE
    """
    GAIT_AMBLE: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_AMBLE: 14>
    GAIT_BOUND: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_BOUND: 12>
    GAIT_CRAWL: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_CRAWL: 29>
    GAIT_DEFAULT: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_DEFAULT: 99>
    GAIT_DOWN_CLIMB_STAIRS: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_DOWN_CLIMB_STAIRS: 9>
    GAIT_ENTER_RL: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_ENTER_RL: 1001>
    GAIT_LOWLEVL_SDK: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_LOWLEVL_SDK: 30>
    GAIT_NONE: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_NONE: 9999>
    GAIT_PASSIVE: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_PASSIVE: 0>
    GAIT_PRONK: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_PRONK: 11>
    GAIT_RL_FALL_RECOVERY: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_RL_FALL_RECOVERY: 111>
    GAIT_RL_FOOT_STAND: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_RL_FOOT_STAND: 113>
    GAIT_RL_HAND_STAND: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_RL_HAND_STAND: 112>
    GAIT_RL_TERRAIN: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_RL_TERRAIN: 110>
    GAIT_RUN_FAST: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_RUN_FAST: 8>
    GAIT_STAND_B: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_STAND_B: 3>
    GAIT_STAND_R: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_STAND_R: 2>
    GAIT_TROT: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_TROT: 10>
    GAIT_UP_CLIMB_STAIRS: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_UP_CLIMB_STAIRS: 56>
    GAIT_WALK: typing.ClassVar[GaitMode]  # value = <GaitMode.GAIT_WALK: 39>
    __members__: typing.ClassVar[dict[str, GaitMode]]  # value = {'GAIT_PASSIVE': <GaitMode.GAIT_PASSIVE: 0>, 'GAIT_STAND_R': <GaitMode.GAIT_STAND_R: 2>, 'GAIT_STAND_B': <GaitMode.GAIT_STAND_B: 3>, 'GAIT_RUN_FAST': <GaitMode.GAIT_RUN_FAST: 8>, 'GAIT_DOWN_CLIMB_STAIRS': <GaitMode.GAIT_DOWN_CLIMB_STAIRS: 9>, 'GAIT_TROT': <GaitMode.GAIT_TROT: 10>, 'GAIT_PRONK': <GaitMode.GAIT_PRONK: 11>, 'GAIT_BOUND': <GaitMode.GAIT_BOUND: 12>, 'GAIT_AMBLE': <GaitMode.GAIT_AMBLE: 14>, 'GAIT_CRAWL': <GaitMode.GAIT_CRAWL: 29>, 'GAIT_LOWLEVL_SDK': <GaitMode.GAIT_LOWLEVL_SDK: 30>, 'GAIT_WALK': <GaitMode.GAIT_WALK: 39>, 'GAIT_UP_CLIMB_STAIRS': <GaitMode.GAIT_UP_CLIMB_STAIRS: 56>, 'GAIT_RL_TERRAIN': <GaitMode.GAIT_RL_TERRAIN: 110>, 'GAIT_RL_FALL_RECOVERY': <GaitMode.GAIT_RL_FALL_RECOVERY: 111>, 'GAIT_RL_HAND_STAND': <GaitMode.GAIT_RL_HAND_STAND: 112>, 'GAIT_RL_FOOT_STAND': <GaitMode.GAIT_RL_FOOT_STAND: 113>, 'GAIT_ENTER_RL': <GaitMode.GAIT_ENTER_RL: 1001>, 'GAIT_DEFAULT': <GaitMode.GAIT_DEFAULT: 99>, 'GAIT_NONE': <GaitMode.GAIT_NONE: 9999>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class GetSpeechConfig:
    bot_config: BotConfig
    dialog_config: DialogConfig
    speaker_config: SpeakerConfig
    tts_type: TtsType
    wakeup_config: WakeupConfig
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class Header:
    frame_id: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def stamp(self) -> int:
        ...
    @stamp.setter
    def stamp(self, arg0: typing.SupportsInt) -> None:
        ...
class HighLevelMotionController:
    def __init__(self) -> None:
        ...
    def execute_trick(self, arg0: TrickAction) -> Status:
        ...
    def get_gait(self) -> GaitMode:
        """
        Get current gait mode, returns gait mode on success, GAIT_NONE on failure
        """
    def initialize(self) -> bool:
        ...
    def send_joystick_command(self, arg0: JoystickCommand) -> Status:
        ...
    def set_gait(self, arg0: GaitMode) -> Status:
        ...
    def shutdown(self) -> None:
        ...
class Image:
    data: Uint8Vector
    encoding: str
    header: Header
    is_bigendian: bool
    def __copy__(self) -> Image:
        ...
    def __deepcopy__(self, arg0: dict) -> Image:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get image data byte count
        """
    def __repr__(self) -> str:
        ...
    @property
    def height(self) -> int:
        ...
    @height.setter
    def height(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def step(self) -> int:
        ...
    @step.setter
    def step(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def width(self) -> int:
        ...
    @width.setter
    def width(self, arg0: typing.SupportsInt) -> None:
        ...
class Imu:
    angular_velocity: Double3Array
    linear_acceleration: Double3Array
    orientation: Double4Array
    def __copy__(self) -> Imu:
        ...
    def __deepcopy__(self, arg0: dict) -> Imu:
        ...
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def temperature(self) -> float:
        ...
    @temperature.setter
    def temperature(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def timestamp(self) -> int:
        ...
    @timestamp.setter
    def timestamp(self, arg0: typing.SupportsInt) -> None:
        ...
class Int8:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def data(self) -> int:
        ...
    @data.setter
    def data(self, arg0: typing.SupportsInt) -> None:
        ...
class JoystickCommand:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def left_x_axis(self) -> float:
        ...
    @left_x_axis.setter
    def left_x_axis(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def left_y_axis(self) -> float:
        ...
    @left_y_axis.setter
    def left_y_axis(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def right_x_axis(self) -> float:
        ...
    @right_x_axis.setter
    def right_x_axis(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def right_y_axis(self) -> float:
        ...
    @right_y_axis.setter
    def right_y_axis(self, arg0: typing.SupportsFloat) -> None:
        ...
class LaserScan:
    header: Header
    intensities: DoubleVector
    ranges: DoubleVector
    def __copy__(self) -> LaserScan:
        ...
    def __deepcopy__(self, arg0: dict) -> LaserScan:
        ...
    def __init__(self) -> None:
        ...
    def __len__(self) -> int:
        """
        Get number of laser scan points
        """
    def __repr__(self) -> str:
        ...
    @property
    def angle_increment(self) -> int:
        ...
    @angle_increment.setter
    def angle_increment(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def angle_max(self) -> int:
        ...
    @angle_max.setter
    def angle_max(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def angle_min(self) -> int:
        ...
    @angle_min.setter
    def angle_min(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def range_max(self) -> int:
        ...
    @range_max.setter
    def range_max(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def range_min(self) -> int:
        ...
    @range_min.setter
    def range_min(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def scan_time(self) -> int:
        ...
    @scan_time.setter
    def scan_time(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def time_increment(self) -> int:
        ...
    @time_increment.setter
    def time_increment(self, arg0: typing.SupportsInt) -> None:
        ...
class LegJointCommand:
    cmd: LegJointCommandArray
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def timestamp(self) -> int:
        ...
    @timestamp.setter
    def timestamp(self, arg0: typing.SupportsInt) -> None:
        ...
class LegJointCommandArray:
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ...) -> None:
        ...
class LegJointStateArray:
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ...) -> None:
        ...
class LegState:
    state: LegJointStateArray
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def timestamp(self) -> int:
        ...
    @timestamp.setter
    def timestamp(self, arg0: typing.SupportsInt) -> None:
        ...
class LowLevelMotionController:
    def __init__(self) -> None:
        ...
    def enable_send_msg(self, arg0: bool) -> None:
        ...
    def initialize(self) -> bool:
        ...
    def publish_leg_command(self, arg0: LegJointCommand) -> Status:
        ...
    def set_period_ms(self, arg0: typing.SupportsInt) -> None:
        ...
    def shutdown(self) -> None:
        ...
    def subscribe_leg_state(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to leg state data
        """
class MagicRobot:
    def __init__(self) -> None:
        ...
    def connect(self) -> Status:
        ...
    def disconnect(self) -> Status:
        ...
    def get_audio_controller(self) -> AudioController:
        ...
    def get_high_level_motion_controller(self) -> HighLevelMotionController:
        ...
    def get_low_level_motion_controller(self) -> LowLevelMotionController:
        ...
    def get_motion_control_level(self) -> ControllerLevel:
        ...
    def get_sdk_version(self) -> str:
        ...
    def get_sensor_controller(self) -> SensorController:
        ...
    def get_state_monitor(self) -> StateMonitor:
        ...
    def initialize(self, arg0: str) -> bool:
        ...
    def set_motion_control_level(self, arg0: ControllerLevel) -> Status:
        ...
    def set_timeout(self, arg0: typing.SupportsInt) -> None:
        ...
    def shutdown(self) -> None:
        ...
class MultiArrayDimension:
    label: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def size(self) -> int:
        ...
    @size.setter
    def size(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def stride(self) -> int:
        ...
    @stride.setter
    def stride(self, arg0: typing.SupportsInt) -> None:
        ...
class MultiArrayDimensionVector:
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> MultiArrayDimensionVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: MultiArrayDimensionVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ...) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: MultiArrayDimensionVector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: ...) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: MultiArrayDimensionVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: ...) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ...:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> ...:
        """
        Remove and return the item at index ``i``
        """
class MultiArrayLayout:
    dim: MultiArrayDimensionVector
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def data_offset(self) -> int:
        ...
    @data_offset.setter
    def data_offset(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def dim_size(self) -> int:
        ...
    @dim_size.setter
    def dim_size(self, arg0: typing.SupportsInt) -> None:
        ...
class PointCloud2:
    data: Uint8Vector
    fields: PointFieldVector
    header: Header
    is_bigendian: bool
    is_dense: bool
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def height(self) -> int:
        ...
    @height.setter
    def height(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def point_step(self) -> int:
        ...
    @point_step.setter
    def point_step(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def row_step(self) -> int:
        ...
    @row_step.setter
    def row_step(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def width(self) -> int:
        ...
    @width.setter
    def width(self, arg0: typing.SupportsInt) -> None:
        ...
class PointField:
    name: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def count(self) -> int:
        ...
    @count.setter
    def count(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def datatype(self) -> int:
        ...
    @datatype.setter
    def datatype(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def offset(self) -> int:
        ...
    @offset.setter
    def offset(self, arg0: typing.SupportsInt) -> None:
        ...
class PointFieldVector:
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, s: slice) -> PointFieldVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: PointFieldVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[...]:
        ...
    def __len__(self) -> int:
        ...
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: ...) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: PointFieldVector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: ...) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: PointFieldVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: ...) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> ...:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> ...:
        """
        Remove and return the item at index ``i``
        """
class PowerSupplyStatus:
    """
    Members:
    
      UNKNOWN
    
      CHARGING
    
      DISCHARGING
    
      NOTCHARGING
    
      FULL
    """
    CHARGING: typing.ClassVar[PowerSupplyStatus]  # value = <PowerSupplyStatus.CHARGING: 1>
    DISCHARGING: typing.ClassVar[PowerSupplyStatus]  # value = <PowerSupplyStatus.DISCHARGING: 2>
    FULL: typing.ClassVar[PowerSupplyStatus]  # value = <PowerSupplyStatus.FULL: 4>
    NOTCHARGING: typing.ClassVar[PowerSupplyStatus]  # value = <PowerSupplyStatus.NOTCHARGING: 3>
    UNKNOWN: typing.ClassVar[PowerSupplyStatus]  # value = <PowerSupplyStatus.UNKNOWN: 0>
    __members__: typing.ClassVar[dict[str, PowerSupplyStatus]]  # value = {'UNKNOWN': <PowerSupplyStatus.UNKNOWN: 0>, 'CHARGING': <PowerSupplyStatus.CHARGING: 1>, 'DISCHARGING': <PowerSupplyStatus.DISCHARGING: 2>, 'NOTCHARGING': <PowerSupplyStatus.NOTCHARGING: 3>, 'FULL': <PowerSupplyStatus.FULL: 4>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class RobotState:
    bms_data: BmsData
    faults: FaultVector
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class S2DString:
    def __getitem__(self, arg0: typing.SupportsInt) -> str:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        ...
    def __setitem__(self, arg0: typing.SupportsInt, arg1: str) -> None:
        ...
class S2DStringVector:
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def __contains__(*args, **kwargs) -> bool:
        """
        Return true the container contains ``x``
        """
    @staticmethod
    @typing.overload
    def __setitem__(*args, **kwargs) -> None:
        ...
    @staticmethod
    def append(*args, **kwargs) -> None:
        """
        Add an item to the end of the list
        """
    @staticmethod
    def count(*args, **kwargs) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @staticmethod
    def insert(*args, **kwargs) -> None:
        """
        Insert an item at a given position.
        """
    @staticmethod
    def remove(*args, **kwargs) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: S2DStringVector) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> S2DStringVector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> ...:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: S2DStringVector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[..., ..., ..., ...]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: S2DStringVector) -> bool:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: S2DStringVector) -> None:
        """
        Assign list elements using a slice object
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    @typing.overload
    def extend(self, L: S2DStringVector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def pop(self) -> ...:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> ...:
        """
        Remove and return the item at index ``i``
        """
class SensorController:
    def __init__(self) -> None:
        ...
    def close_binocular_camera(self) -> Status:
        ...
    def close_channel_switch(self) -> Status:
        ...
    def close_laser_scan(self) -> Status:
        ...
    def close_rgbd_camera(self) -> Status:
        ...
    def initialize(self) -> bool:
        ...
    def open_binocular_camera(self) -> Status:
        ...
    def open_channel_switch(self) -> Status:
        ...
    def open_laser_scan(self) -> Status:
        ...
    def open_rgbd_camera(self) -> Status:
        ...
    def shutdown(self) -> None:
        ...
    def subscribe_depth_image(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to depth image data
        """
    def subscribe_head_touch(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to head touch data
        """
    def subscribe_imu(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to IMU data
        """
    def subscribe_laser_scan(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to laser scan data
        """
    def subscribe_left_binocular_high_img(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to left high-quality binocular data
        """
    def subscribe_left_binocular_low_img(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to left low-quality binocular data
        """
    def subscribe_rgb_depth_camera_info(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to RGBD depth camera intrinsic data
        """
    def subscribe_rgbd_color_camera_info(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to RGBD color camera intrinsic data
        """
    def subscribe_rgbd_color_image(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to RGBD color image data
        """
    def subscribe_rgbd_depth_image(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to RGBD depth image data
        """
    def subscribe_right_binocular_low_img(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to right low-quality binocular data
        """
    def subscribe_tof(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to TOF data
        """
    def subscribe_ultra(self, arg0: collections.abc.Callable) -> None:
        """
        Subscribe to ultrasonic data
        """
class SetSpeechConfig:
    bot_id: str
    custom_bot: StringCustomBotMap
    is_doa_enable: bool
    is_enable: bool
    is_front_doa: bool
    is_fullduplex_enable: bool
    region: str
    speaker_id: str
    wakeup_name: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def speaker_speed(self) -> float:
        ...
    @speaker_speed.setter
    def speaker_speed(self, arg0: typing.SupportsFloat) -> None:
        ...
class SingleLegJointCommand:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def dq_des(self) -> float:
        ...
    @dq_des.setter
    def dq_des(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def kd(self) -> float:
        ...
    @kd.setter
    def kd(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def kp(self) -> float:
        ...
    @kp.setter
    def kp(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def q_des(self) -> float:
        ...
    @q_des.setter
    def q_des(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def tau_des(self) -> float:
        ...
    @tau_des.setter
    def tau_des(self, arg1: typing.SupportsFloat) -> None:
        ...
class SingleLegJointState:
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def dq(self) -> float:
        ...
    @dq.setter
    def dq(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def q(self) -> float:
        ...
    @q.setter
    def q(self, arg1: typing.SupportsFloat) -> None:
        ...
    @property
    def tau_est(self) -> float:
        ...
    @tau_est.setter
    def tau_est(self, arg1: typing.SupportsFloat) -> None:
        ...
class SpeakerConfig:
    data: String2DStringVectorMap
    selected: SpeakerConfigSelected
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def speaker_speed(self) -> float:
        ...
    @speaker_speed.setter
    def speaker_speed(self, arg0: typing.SupportsFloat) -> None:
        ...
class SpeakerConfigSelected:
    region: str
    speaker_id: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class StateMonitor:
    def __init__(self) -> None:
        ...
    def get_current_state(self) -> RobotState:
        """
        Get current robot running state
        """
    def initialize(self) -> bool:
        ...
    def shutdown(self) -> None:
        ...
class Status:
    code: ErrorCode
    message: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class String2DStringVectorMap:
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> S2DStringVector:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: S2DStringVector) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class StringBotConfigMap:
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> ...:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: ...) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class StringBotInfoMap:
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> ...:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: ...) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class StringCustomBotMap:
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> ...:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: ...) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class StringStringMap:
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> str:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this map.
        """
    def __setitem__(self, arg0: str, arg1: str) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class TrickAction:
    """
    Members:
    
      ACTION_NONE
    
      ACTION_WIGGLE_HIP
    
      ACTION_SWING_BODY
    
      ACTION_STRETCH
    
      ACTION_STOMP
    
      ACTION_JUMP_JACK
    
      ACTION_SPACE_WALK
    
      ACTION_IMITATE
    
      ACTION_SHAKE_HEAD
    
      ACTION_PUSH_UP
    
      ACTION_CHEER_UP
    
      ACTION_HIGH_FIVES
    
      ACTION_SCRATCH
    
      ACTION_HIGH_JUMP
    
      ACTION_SWING_DANCE
    
      ACTION_LEAP_FROG
    
      ACTION_BACK_FLIP
    
      ACTION_FRONT_FLIP
    
      ACTION_SPIN_JUMP_LEFT
    
      ACTION_SPIN_JUMP_RIGHT
    
      ACTION_JUMP_FRONT
    
      ACTION_ACT_CUTE
    
      ACTION_BOXING
    
      ACTION_SIDE_SOMERSAULT
    
      ACTION_RANDOM_DANCE
    
      ACTION_LEFT_SIDE_SOMERSAULT
    
      ACTION_RIGHT_SIDE_SOMERSAULT
    
      ACTION_DANCE2
    
      ACTION_EMERGENCY_STOP
    
      ACTION_LIE_DOWN
    
      ACTION_RECOVERY_STAND
    
      ACTION_HAPPY_NEW_YEAR
    
      ACTION_SLOW_GO_FRONT
    
      ACTION_SLOW_GO_BACK
    
      ACTION_BACK_HOME
    
      ACTION_LEAVE_HOME
    
      ACTION_TURN_AROUND
    
      ACTION_DANCE
    
      ACTION_ROLL_ABOUT
    
      ACTION_SHAKE_RIGHT_HAND
    
      ACTION_SHAKE_LEFT_HAND
    
      ACTION_SIT_DOWN
    """
    ACTION_ACT_CUTE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_ACT_CUTE: 46>
    ACTION_BACK_FLIP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_BACK_FLIP: 41>
    ACTION_BACK_HOME: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_BACK_HOME: 110>
    ACTION_BOXING: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_BOXING: 47>
    ACTION_CHEER_UP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_CHEER_UP: 35>
    ACTION_DANCE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_DANCE: 115>
    ACTION_DANCE2: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_DANCE2: 91>
    ACTION_EMERGENCY_STOP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_EMERGENCY_STOP: 101>
    ACTION_FRONT_FLIP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_FRONT_FLIP: 42>
    ACTION_HAPPY_NEW_YEAR: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_HAPPY_NEW_YEAR: 105>
    ACTION_HIGH_FIVES: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_HIGH_FIVES: 36>
    ACTION_HIGH_JUMP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_HIGH_JUMP: 38>
    ACTION_IMITATE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_IMITATE: 32>
    ACTION_JUMP_FRONT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_JUMP_FRONT: 45>
    ACTION_JUMP_JACK: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_JUMP_JACK: 30>
    ACTION_LEAP_FROG: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_LEAP_FROG: 40>
    ACTION_LEAVE_HOME: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_LEAVE_HOME: 111>
    ACTION_LEFT_SIDE_SOMERSAULT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_LEFT_SIDE_SOMERSAULT: 84>
    ACTION_LIE_DOWN: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_LIE_DOWN: 102>
    ACTION_NONE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_NONE: 0>
    ACTION_PUSH_UP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_PUSH_UP: 34>
    ACTION_RANDOM_DANCE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_RANDOM_DANCE: 49>
    ACTION_RECOVERY_STAND: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_RECOVERY_STAND: 103>
    ACTION_RIGHT_SIDE_SOMERSAULT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_RIGHT_SIDE_SOMERSAULT: 85>
    ACTION_ROLL_ABOUT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_ROLL_ABOUT: 116>
    ACTION_SCRATCH: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SCRATCH: 37>
    ACTION_SHAKE_HEAD: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SHAKE_HEAD: 33>
    ACTION_SHAKE_LEFT_HAND: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SHAKE_LEFT_HAND: 118>
    ACTION_SHAKE_RIGHT_HAND: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SHAKE_RIGHT_HAND: 117>
    ACTION_SIDE_SOMERSAULT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SIDE_SOMERSAULT: 48>
    ACTION_SIT_DOWN: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SIT_DOWN: 119>
    ACTION_SLOW_GO_BACK: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SLOW_GO_BACK: 109>
    ACTION_SLOW_GO_FRONT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SLOW_GO_FRONT: 108>
    ACTION_SPACE_WALK: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SPACE_WALK: 31>
    ACTION_SPIN_JUMP_LEFT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SPIN_JUMP_LEFT: 43>
    ACTION_SPIN_JUMP_RIGHT: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SPIN_JUMP_RIGHT: 44>
    ACTION_STOMP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_STOMP: 29>
    ACTION_STRETCH: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_STRETCH: 28>
    ACTION_SWING_BODY: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SWING_BODY: 27>
    ACTION_SWING_DANCE: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_SWING_DANCE: 39>
    ACTION_TURN_AROUND: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_TURN_AROUND: 112>
    ACTION_WIGGLE_HIP: typing.ClassVar[TrickAction]  # value = <TrickAction.ACTION_WIGGLE_HIP: 26>
    __members__: typing.ClassVar[dict[str, TrickAction]]  # value = {'ACTION_NONE': <TrickAction.ACTION_NONE: 0>, 'ACTION_WIGGLE_HIP': <TrickAction.ACTION_WIGGLE_HIP: 26>, 'ACTION_SWING_BODY': <TrickAction.ACTION_SWING_BODY: 27>, 'ACTION_STRETCH': <TrickAction.ACTION_STRETCH: 28>, 'ACTION_STOMP': <TrickAction.ACTION_STOMP: 29>, 'ACTION_JUMP_JACK': <TrickAction.ACTION_JUMP_JACK: 30>, 'ACTION_SPACE_WALK': <TrickAction.ACTION_SPACE_WALK: 31>, 'ACTION_IMITATE': <TrickAction.ACTION_IMITATE: 32>, 'ACTION_SHAKE_HEAD': <TrickAction.ACTION_SHAKE_HEAD: 33>, 'ACTION_PUSH_UP': <TrickAction.ACTION_PUSH_UP: 34>, 'ACTION_CHEER_UP': <TrickAction.ACTION_CHEER_UP: 35>, 'ACTION_HIGH_FIVES': <TrickAction.ACTION_HIGH_FIVES: 36>, 'ACTION_SCRATCH': <TrickAction.ACTION_SCRATCH: 37>, 'ACTION_HIGH_JUMP': <TrickAction.ACTION_HIGH_JUMP: 38>, 'ACTION_SWING_DANCE': <TrickAction.ACTION_SWING_DANCE: 39>, 'ACTION_LEAP_FROG': <TrickAction.ACTION_LEAP_FROG: 40>, 'ACTION_BACK_FLIP': <TrickAction.ACTION_BACK_FLIP: 41>, 'ACTION_FRONT_FLIP': <TrickAction.ACTION_FRONT_FLIP: 42>, 'ACTION_SPIN_JUMP_LEFT': <TrickAction.ACTION_SPIN_JUMP_LEFT: 43>, 'ACTION_SPIN_JUMP_RIGHT': <TrickAction.ACTION_SPIN_JUMP_RIGHT: 44>, 'ACTION_JUMP_FRONT': <TrickAction.ACTION_JUMP_FRONT: 45>, 'ACTION_ACT_CUTE': <TrickAction.ACTION_ACT_CUTE: 46>, 'ACTION_BOXING': <TrickAction.ACTION_BOXING: 47>, 'ACTION_SIDE_SOMERSAULT': <TrickAction.ACTION_SIDE_SOMERSAULT: 48>, 'ACTION_RANDOM_DANCE': <TrickAction.ACTION_RANDOM_DANCE: 49>, 'ACTION_LEFT_SIDE_SOMERSAULT': <TrickAction.ACTION_LEFT_SIDE_SOMERSAULT: 84>, 'ACTION_RIGHT_SIDE_SOMERSAULT': <TrickAction.ACTION_RIGHT_SIDE_SOMERSAULT: 85>, 'ACTION_DANCE2': <TrickAction.ACTION_DANCE2: 91>, 'ACTION_EMERGENCY_STOP': <TrickAction.ACTION_EMERGENCY_STOP: 101>, 'ACTION_LIE_DOWN': <TrickAction.ACTION_LIE_DOWN: 102>, 'ACTION_RECOVERY_STAND': <TrickAction.ACTION_RECOVERY_STAND: 103>, 'ACTION_HAPPY_NEW_YEAR': <TrickAction.ACTION_HAPPY_NEW_YEAR: 105>, 'ACTION_SLOW_GO_FRONT': <TrickAction.ACTION_SLOW_GO_FRONT: 108>, 'ACTION_SLOW_GO_BACK': <TrickAction.ACTION_SLOW_GO_BACK: 109>, 'ACTION_BACK_HOME': <TrickAction.ACTION_BACK_HOME: 110>, 'ACTION_LEAVE_HOME': <TrickAction.ACTION_LEAVE_HOME: 111>, 'ACTION_TURN_AROUND': <TrickAction.ACTION_TURN_AROUND: 112>, 'ACTION_DANCE': <TrickAction.ACTION_DANCE: 115>, 'ACTION_ROLL_ABOUT': <TrickAction.ACTION_ROLL_ABOUT: 116>, 'ACTION_SHAKE_RIGHT_HAND': <TrickAction.ACTION_SHAKE_RIGHT_HAND: 117>, 'ACTION_SHAKE_LEFT_HAND': <TrickAction.ACTION_SHAKE_LEFT_HAND: 118>, 'ACTION_SIT_DOWN': <TrickAction.ACTION_SIT_DOWN: 119>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TrinocularCameraFrame:
    header: Header
    imgf_array: Uint8Vector
    imgfl_array: Uint8Vector
    imgfr_array: Uint8Vector
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def decode_time(self) -> int:
        ...
    @decode_time.setter
    def decode_time(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def vin_time(self) -> int:
        ...
    @vin_time.setter
    def vin_time(self, arg0: typing.SupportsInt) -> None:
        ...
class TtsCommand:
    content: str
    id: str
    mode: TtsMode
    priority: TtsPriority
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
class TtsMode:
    """
    Members:
    
      CLEARTOP
    
      ADD
    
      CLEARBUFFER
    """
    ADD: typing.ClassVar[TtsMode]  # value = <TtsMode.ADD: 1>
    CLEARBUFFER: typing.ClassVar[TtsMode]  # value = <TtsMode.CLEARBUFFER: 2>
    CLEARTOP: typing.ClassVar[TtsMode]  # value = <TtsMode.CLEARTOP: 0>
    __members__: typing.ClassVar[dict[str, TtsMode]]  # value = {'CLEARTOP': <TtsMode.CLEARTOP: 0>, 'ADD': <TtsMode.ADD: 1>, 'CLEARBUFFER': <TtsMode.CLEARBUFFER: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TtsPriority:
    """
    Members:
    
      HIGH
    
      MIDDLE
    
      LOW
    """
    HIGH: typing.ClassVar[TtsPriority]  # value = <TtsPriority.HIGH: 0>
    LOW: typing.ClassVar[TtsPriority]  # value = <TtsPriority.LOW: 2>
    MIDDLE: typing.ClassVar[TtsPriority]  # value = <TtsPriority.MIDDLE: 1>
    __members__: typing.ClassVar[dict[str, TtsPriority]]  # value = {'HIGH': <TtsPriority.HIGH: 0>, 'MIDDLE': <TtsPriority.MIDDLE: 1>, 'LOW': <TtsPriority.LOW: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class TtsType:
    """
    Members:
    
      NONE
    
      DOUBAO
    
      GOOGLE
    """
    DOUBAO: typing.ClassVar[TtsType]  # value = <TtsType.DOUBAO: 1>
    GOOGLE: typing.ClassVar[TtsType]  # value = <TtsType.GOOGLE: 2>
    NONE: typing.ClassVar[TtsType]  # value = <TtsType.NONE: 0>
    __members__: typing.ClassVar[dict[str, TtsType]]  # value = {'NONE': <TtsType.NONE: 0>, 'DOUBAO': <TtsType.DOUBAO: 1>, 'GOOGLE': <TtsType.GOOGLE: 2>}
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Uint8Vector:
    __hash__: typing.ClassVar[None] = None
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: typing.SupportsInt) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: typing.SupportsInt) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: Uint8Vector) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> Uint8Vector:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: typing.SupportsInt) -> int:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: Uint8Vector) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: collections.abc.Iterable) -> None:
        ...
    def __iter__(self) -> collections.abc.Iterator[int]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: Uint8Vector) -> bool:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: typing.SupportsInt, arg1: typing.SupportsInt) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: Uint8Vector) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: typing.SupportsInt) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: typing.SupportsInt) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: Uint8Vector) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: collections.abc.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: typing.SupportsInt, x: typing.SupportsInt) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> int:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: typing.SupportsInt) -> int:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: typing.SupportsInt) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class WakeupConfig:
    data: StringStringMap
    name: str
    def __init__(self) -> None:
        ...
    def __repr__(self) -> str:
        ...
LEG_JOINT_NUM: int = 12
PERIOD_MS: int = 2
