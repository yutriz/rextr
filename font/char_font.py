import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

from font.image_utils import image_to_byte_array, create_character_shadow

SHOW_IMAGE = 0

class CharFont:
    def __init__(
        self, cfont, size: int=12, 
        top_left_pos: tuple=(0, 0)
    ):
        self._font_meta = cfont
        self.top_left_pos = top_left_pos
        self.size = size

    def character_image(
        self, 
        chara: str,
        size: Optional[int] = None,  # font size 
        w: int = -1, h: int = -1,       # canvas size
        top_left_pos: Optional[tuple] = None,
        mode: str = "L",
        backgroud_color = "black",
        charecter_shadow = True,
        shadow_offset = (0,1)
    ) -> Image:
        """
            @param: mode, 'L' (8 bits) or '1' (1 bits) 
            ref: https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes
        """
        assert(mode in ['L', '1'])
        assert(backgroud_color in ["black", "white"])

        if not top_left_pos:
            top_left_pos = self.top_left_pos
        if not size:
            size = self.size

        if w == -1 or h == -1:
            canvas_size = (size, size)
        else:
            canvas_size = (w, h)

        if backgroud_color == "black":
            font_fill_color = "white"
        elif backgroud_color == "white":
            font_fill_color = "black"
        
        font = ImageFont.truetype(self._font_meta, size=size)

        canvas = Image.new(mode, canvas_size, color=backgroud_color)
        draw_char = ImageDraw.Draw(canvas)
        draw_char.text(top_left_pos, chara, font=font, fill=font_fill_color)

        if charecter_shadow:
            shadowed = create_character_shadow(
                np.asarray(canvas), 
                offset=shadow_offset
            )

            canvas = Image.fromarray(shadowed)

        if SHOW_IMAGE:
            canvas.show()
            
        return canvas

    # def char_image_in_byte_array(
    #         self, 
    #         chara: str,
    #         bit_depth = 2,
    #         size: Optional[int] = None,  # font size 
    #         w: int = -1, h: int = -1,    # canvas size
    #         top_left_pos: Optional[tuple] = None,
    #         mode: str = "L"
    #     ):  
        
    #     image_np = np.asarray(
    #         self.character_image(
    #             chara, 
    #             size, 
    #             w, h, 
    #             top_left_pos, 
    #             mode
    #         )
    #     )

    #     return image_to_byte_array(image_np, bit_depth=bit_depth)