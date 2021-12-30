from enum import Enum

class ScoreAttrType(Enum):
    Min = 0     # If the score goes from -1.0 to 0.0
    Max = 1     # If the score goes from 0.0 to 1.0
    MinMax = 2  # If the score goes from -1.0 to 1.0

# Score analysis attributes
SCORE_ATTRIBUTES = {
    'behavioral': ScoreAttrType.Max,
    'curation': ScoreAttrType.Max,
    'failure': ScoreAttrType.Min,
    'harmonious_color': ScoreAttrType.MinMax,
    'highlight_visibility': ScoreAttrType.Max,
    'immersiveness': ScoreAttrType.Max,
    'interaction': ScoreAttrType.Max,
    'interesting_subject': ScoreAttrType.MinMax,
    'intrusive_object_presence': ScoreAttrType.Min,
    'lively_color': ScoreAttrType.MinMax,
    'low_light': ScoreAttrType.Max,
    'noise': ScoreAttrType.Min,
    'overall': ScoreAttrType.Max,
    'pleasant_camera_tilt': ScoreAttrType.MinMax,
    'pleasant_composition': ScoreAttrType.MinMax,
    'pleasant_lighting': ScoreAttrType.MinMax,
    'pleasant_pattern': ScoreAttrType.Max,
    'pleasant_perspective': ScoreAttrType.MinMax,
    'pleasant_post_processing': ScoreAttrType.MinMax,
    'pleasant_reflection': ScoreAttrType.MinMax,
    'pleasant_symmetry': ScoreAttrType.Max,
    'promotion': ScoreAttrType.Max,
    'sharply_focused_subject': ScoreAttrType.Max,
    'tastefully_blurred': ScoreAttrType.MinMax,
    'well_chosen_subject': ScoreAttrType.MinMax,
    'well_framed_subject': ScoreAttrType.MinMax,
    'well_timed_shot': ScoreAttrType.MinMax,
}