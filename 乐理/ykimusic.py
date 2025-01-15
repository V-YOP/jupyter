"""
乐理抽象，目的是熟悉python的操作符重载以及在后面学习乐理的时候方便，提供：

Pitch：音高，如 C#4，Db，有一个可选的八度
Interval：音程，音高的差
Chord：和弦，音高的乘积
"""

from functools import total_ordering
import re
from typing import Literal, Optional, overload

@total_ordering
class Pitch:
    __LETTER_STEP = dict(C=0,D=2,E=4,F=5,G=7,A=9,B=11)
    LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    """音符类"""
    @staticmethod
    def parse(name: str) -> Optional[tuple[str, Optional[str], Optional[int]]]:
        """解析音符名称，返回音名、修饰符、音高，返回None如果解析失败"""
        if name is None:
            raise ValueError('name cannot be None')
        REGEX = r'([CDEFGABcdefgab])(#*|b*)([0-7])?'        
        if not (match := re.fullmatch(REGEX, name)):
            return None
        
        letter, accidental, octave = match.groups()
        if octave is not None:
            octave = int(octave)
        return letter.upper(), accidental, octave

    def __init__(self, v: str) -> None:
        if not (result := Pitch.parse(v)):
            raise ValueError(f"Invalid pitch '{v}'")
        letter, accidental, octave = result
        self.__letter = letter
        self.__accidental = accidental
        self.__octave = octave

    @property
    def step(self):
        """返回音高对应的实际半音数，以C为基准，C返回0，B返回11；注意Cb返回11"""
        original_step = Pitch.__LETTER_STEP[self.letter]
        if self.accidental is None:
            return original_step
        return original_step - self.accidental.count('b') + self.accidental.count('#')
        
    @property
    def letter(self):
        return self.__letter
    
    @property
    def accidental(self):
        return self.__accidental
    
    @property
    def octave(self):
        return self.__octave
    
    @property
    def index(self):
        """返回自己以C为0开始的度数，C=0，D=1, B=6"""
        return Pitch.LETTERS.index(self.letter)

    def __repr__(self) -> str:
        return f"Note('{self}')"

    def __str__(self) -> str:
        return f'{self.letter}{self.accidental or ''}{self.octave or ''}'
    
    def __hash__(self) -> int:
        return hash((self.accidental, self.letter, self.octave))

    def __eq__(self, value):
        if not isinstance(value, Pitch):
            return False
        return self.accidental == value.accidental and self.letter == value.letter and self.octave == value.octave

    def __lt__(self, value):
        if not isinstance(value, Pitch):
            return NotImplemented
        return (self.octave or 4, self.step) < (value.octave or 4, value.step)

    @overload
    def __add__(self, value: 'Interval') -> 'Pitch': 
        """将音高增加该音程"""
    @overload
    def __add__(self, value: str) -> 'Pitch': 
        """将音高增加该音程"""
    @overload
    def __add__(self, value): ...
    def __add__(self, value):
        if not isinstance(value, Interval) and not isinstance(value, str):
            return NotImplemented
        if isinstance(value, str):
            value = Interval(value)

        res_step = (self.step + value.step) % 12
        octave_offset = (self.step + value.step) // 12
        res_index = (self.index + value.degree - 1) % 7
        # 首先根据degree重新找到letter
        letter = Pitch.LETTERS[res_index]
        letter_step = Pitch.__LETTER_STEP[letter]

        step_diff = letter_step - res_step
        if step_diff == 0:
            modifier = ''
        elif step_diff > 0:
            modifier = 'b' * step_diff
        else:
            modifier = '#' * -step_diff

        octave_str = ''
        if self.octave:
            octave_str = self.octave + octave_offset
        return Pitch(f'{letter}{modifier}{octave_str}')
    
    @overload
    def __sub__(self, value: 'Interval') -> 'Pitch': 
        """将音高减少该音程"""
    @overload
    def __sub__(self, value: 'Pitch') -> 'Interval': 
        """得到两个音高的差，注意这里不处理正负性"""
    @overload
    def __sub__(self, value: str) -> 'Pitch': 
        """将音高减少该音程"""
    @overload
    def __sub__(self, value): ...
    def __sub__(self, value):
        # if not isinstance(value, Interval) and not isinstance(value, str):
        #     return NotImplemented
        # if isinstance(value, str):
        #     value = Interval(value)
        # # 先检查音程是否大于八度
        ...

@total_ordering
class Interval:
    """音程类"""

    @staticmethod
    def parse(name: str) -> Optional[tuple[str, int]]:
        """解析音程名称，返回修饰符，度数，返回None如果解析失败"""
        if name is None:
            raise ValueError('name cannot be None')
        REGEX = r'([Mm+-ADP])(\d+)'        
        if not (match := re.fullmatch(REGEX, name)):
            return None
        
        accidental, degree = match.groups()
        if accidental == '+':
            accidental = 'A'
        elif accidental == '-':
            accidental = 'D'
        degree = int(degree)
        if degree % 7 not in (1, 4, 5) and accidental == 'P':
            return None
        
        return accidental, degree

    def __init__(self, v: str) -> None:
        if not (result := Interval.parse(v)):
            raise ValueError(f"Invalid interval '{v}'")
        accidental, degree = result
        self.__accidental = accidental
        self.__degree = degree
    
    @property
    def accidental(self):
        return self.__accidental
    
    @property
    def degree(self):
        return self.__degree
    
    @property
    def step(self):
        """音程对应的半音数"""
        octaves = self.degree // 7 - 1
        mod_degree = (self.degree - 8) % 7 if self.degree > 8 else self.degree
        map = {
            1: 0, 4: 5, 5: 7,
            2: 2, 3: 4, 6: 9, 7: 11, 8: 12
        } # 硬编码各级的音程，其中一、四、五度以纯的算，其他的以大的算

        res = map[mod_degree] + octaves * 12
        if mod_degree in (1, 4, 5, 8):
            if self.accidental == 'P':
                return res
            if self.accidental == 'A':
                return res + 1
            return res - 1
        
        if self.accidental == 'M':
            return res
        if self.accidental == 'm':
            return res - 1
        if self.accidental == 'A':
            return res + 1
        if self.accidental == 'D':
            return res - 2
        raise ValueError(f"cant get step of '{self}'")

    @property
    def single_octave(self):
        """返回该复音程的单音程，如果自己本身就是单音程，返回自己"""
        if self.degree <= 8:
            return self
        return Interval(f'{self.accidental}{(self.degree - 8) % 7}')

    @property
    def inverted(self):
        """返回该音程的转位音程"""
        single_self = self.single_octave

    def __hash__(self) -> int:
        return hash((self.accidental, self.degree))

    def __eq__(self, value):
        if not isinstance(value, Interval):
            return NotImplemented
        return self.accidental == value.accidental and self.degree == value.degree

    def __lt__(self, value):
        if not isinstance(value, Interval):
            return NotImplemented
        return self.step < value.step

    # @overload
    # def __add__(self, value: 'Interval') -> 'Interval': 
    #     """合并两个音程"""
    # @overload
    # def __add__(self, value: str) -> 'Interval': 
    #     """合并两个音程"""
    # def __add__(self, value):
    #     if not isinstance(value, Interval):
    #         return NotImplemented
