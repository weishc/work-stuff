import project


def test_check_prerequest():
    assert project.check_ffmpeg() == True
    assert project.check_models() == True
    assert project.check_Real_ESRGAN_ncnn_Vulkan() == True


def test_get_fps():
    assert project.get_fps(r"crag.mp4").rstrip() == "24/1"


def test_get_frame_count():
    assert project.get_frame_count(r"crag.mp4").rstrip() == "24"
