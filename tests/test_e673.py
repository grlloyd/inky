def test_set_image_p256(GPIO, spidev):
    from PIL import Image

    from inky import inky_e673

    img = Image.new("P", (800, 480))

    for x in range(256):
        img.putpixel((x, x), (x, 0, 0))

    inky = inky_e673.Inky()

    inky.set_image(img)


def _recording_inky(inky_e673, **kwargs):
    inky = inky_e673.Inky(**kwargs)
    inky.setup = lambda: None
    inky._busy_wait = lambda timeout=None: None
    inky.commands = []
    inky._send_command = lambda command, data=None: inky.commands.append((command, data))
    return inky


def test_show_full_has_no_window(GPIO, spidev, smbus2):
    from inky import inky_e673

    inky = _recording_inky(inky_e673)
    inky.show()

    sent = dict(inky.commands)
    assert inky_e673.EL673_PTLW not in sent
    assert len(sent[inky_e673.EL673_DTM1]) == 800 * 480 // 2


def test_show_region_sends_aligned_window(GPIO, spidev, smbus2):
    from inky import inky_e673

    inky = _recording_inky(inky_e673)
    inky.buf[:] = inky.WHITE
    inky.buf[10:20, 5:15] = inky.RED
    inky.show(region=(5, 10, 10, 10))

    cmds = [c for c, _ in inky.commands]
    sent = dict(inky.commands)
    # x 5..14 widens to 4..15, y is unchanged; ends are inclusive
    assert sent[inky_e673.EL673_PTLW] == [0, 4, 0, 15, 0, 10, 0, 19, 0x01]
    assert cmds.index(inky_e673.EL673_PTLW) < cmds.index(inky_e673.EL673_DTM1)
    assert sent[inky_e673.EL673_CDI] == [0xFF]
    assert cmds.index(inky_e673.EL673_CDI) < cmds.index(inky_e673.EL673_DRF)

    data = sent[inky_e673.EL673_DTM1]
    assert len(data) == 12 * 10 // 2
    # first row: white pixel at x=4, then red from x=5
    assert data[0] == (inky.WHITE << 4) | inky.RED


def test_show_region_follows_flip(GPIO, spidev, smbus2):
    from inky import inky_e673

    inky = _recording_inky(inky_e673, v_flip=True)
    inky.show(region=(0, 0, 8, 4))

    # v_flip mirrors columns, so the region lands at the right-hand edge
    assert dict(inky.commands)[inky_e673.EL673_PTLW] == [0x03, 0x18, 0x03, 0x1F, 0, 0, 0, 3, 0x01]


def test_show_region_out_of_bounds(GPIO, spidev, smbus2):
    import pytest

    from inky import inky_e673

    inky = _recording_inky(inky_e673)
    with pytest.raises(ValueError):
        inky.show(region=(790, 0, 20, 10))
