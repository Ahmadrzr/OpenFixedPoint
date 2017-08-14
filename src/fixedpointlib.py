#   Copyright:
#       Copyright 2017 Ahmad RezazadehReyhani
#
#       Licensed under the Apache License, Version 2.0 (the "License");
#       you may not use this file except in compliance with the License.
#       You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#       Unless required by applicable law or agreed to in writing, software
#       distributed under the License is distributed on an "AS IS" BASIS,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#       See the License for the specific language governing permissions and
#       limitations under the License.
#
#   Acknowledgment:
#       Grateful appreciation to the Farhang Wireless Inc. for their support and generously funding the implementation of this library.
#       http://farhangwireless.com/


from numpy import abs, log2, floor, round, inf
from bitstring import Bits


class dtype:
    '''
    Fixedpoint variable types
    int     : signed integer variable
    uint    : unsigned integer variable
    fxp     : signed fractional variable
    uint    : unsigned fractional variable
    float   : floating point variable
    '''
    int   = 'int'
    uint  = 'uint'
    fxp   = 'fxp'
    ufxp  = 'ufxp'
    float = 'float'


class modes:
    '''
    arithmetic operation modes
    FULL        : output width is inferred from operands to keep exact operation results
    FIXEDFRAC   : output integer width grows to fit the results, but fractional width keeps track of significant bits
    FIXEDWIDTH  : output integer width is equal to the maximum of input integer widths, and output fractional width is the minimum of input fractional widths
    MANUAL      : output widths will be given by user
    '''
    FULL        = 'FULL'
    FIXEDFRAC   = 'FIXEDFRAC'
    FIXEDWIDTH  = 'FIXEDWIDTH'
    MANUAL      = 'MANUAL'


class FXP:
    '''
    Fixedpoint variable class
    Fixedpoint object has following properties:
    - _val      : the value stored in the object
    - intg      : integer width of the object
    - frac      : fractional width of the object
    - type      : type of the object e.g. int or fxp. will be chosen from dtype class
    - opmode    : defines the mode of the operation if this object is one of the operands
    - sat       : if set to True, saturates the output value of operation to maximum/minimum value of given bit width, otherwise output will wrap around
    - round     : if set to True, output will be rounded when removing fractional bits, otherwise output will be truncated

    FXP object can be generated using two methods:
        - pass a value and a typle which defines the parameters
            a = FXP(-11.9341, (9,5,dtype.fxp, modes.FIXEDFRAC,False,False))
        - pass a value and another object as template to constructor
            a = FXP(4.23974, another_FXP_object)

    If you need to assign object a to object b then use copy() method to assign an independent copy of a to b otherwise both objects will point to same point
        b = a.copy()
        b = a.copy(template) will generates an object with the value of a, but other parameters will be copied from template (tuple or another FXP object)

    To change a FXP object use convert method and mention the parameter name and new value or pass a template to infer the parameters
        b.convert(opmode=modes.FIXEDFRAC,type=dtype.ufxp)
        b.convert(template=templ)
        if both template and individual parameters are provided, individual parameters will be used and remaining parameters will be copied from template

        def debug(enable=None):
        if(isinstance(enable,bool)):
            FXP._DBG = enable

    To access the equivalent floating point value of the object use val() method.

    Special inputs:
            'inf', float('inf')   : actual value will be maximum possible value of given bit width
            '-inf', -float('inf') : actual value will be minimum possible value of given bit width

    Operands must have same opmode, sat and round settings.
    Fractional width of int and uint type must be zero.
    value of uint and ufxp object must be non-negative.

    Example:
        FXP.debug(True)

        a = FXP(-11.123456789, (9,5,dtype.fxp, modes.FIXEDFRAC,False,False))
        b = FXP(39.987654321, (7,1,dtype.fxp, modes.FIXEDFRAC,False,False))
        i = FXP(-3, (3,0,dtype.int, modes.FIXEDFRAC,False,False))
        u = FXP(+3, (3,0,dtype.uint, modes.FIXEDFRAC,False,False))

        c = FXP('-inf', a)

        av = a.val()

        print(a)

        a.convert(opmode=modes.FIXEDFRAC,type=dtype.ufxp)

        x = a + 2
        y = 2 - a
        z = a * b
    '''
    _DBG      = False

    def __init__(self, val, template):
        '''
        public method
        Class constructor
        val is a floating point value
        template is a tuple or another FXP object
        '''
        self._read_template(template)
        self._set_val(val)

    def _read_template(self, template):
        '''
        private method
        Extracts object parameters from the given template
        '''
        if(isinstance(template, tuple)):
            self.intg   = template[0]
            self.frac   = template[1]
            self.type   = template[2]  # uint, int, fxp, ufxp, float
            self.opmode = template[3]  # FULL, FIXEDFRAC, FIXEDWIDTH
            self.sat    = template[4]  # False, True
            self.round  = template[5]  # False, True
        elif(isinstance(template, FXP)):
            self.intg   = template.intg
            self.frac   = template.frac
            self.type   = template.type
            self.opmode = template.opmode
            self.sat    = template.sat
            self.round  = template.round
        else:
            raise Exception("wrong input format")

    def _set_val(self, val):
        '''
        private method
        sets the internal value of the object based on the given parameters
        saturation/rounding/with set/change is applied in this method
        '''
        pinf = FXP._pinf(self.intg, self.frac, self.type)
        ninf = FXP._ninf(self.intg, self.frac, self.type)
        # special inputs
        if(val == 'inf' or val == float('inf')):
            val = pinf
        if(val == '-inf' or val == -float('inf')):
            val = ninf
        # saturation
        if(self.sat):
            if(val > pinf):
                # if(FXP._DBG):
                    # print(Fore.YELLOW + 'saturation !' + Style.RESET_ALL, self.intg, self.frac, pinf, val)
                val = pinf
            if(val < ninf):
                # if(FXP._DBG):
                    # print(Fore.YELLOW + 'saturation !' + Style.RESET_ALL, self.intg, self.frac, pinf, val)
                val = ninf
        else:
            if(val > pinf):
                # if(FXP._DBG):
                    # print(Fore.RED + 'overflow !' + Style.RESET_ALL, self.intg, self.frac, pinf, val)
                pass
            if(val < ninf):
                # if(FXP._DBG):
                    # print(Fore.RED + 'overflow !' + Style.RESET_ALL, self.intg, self.frac, pinf, val)
                pass
        if(self.type == dtype.float):
            self._val = val
        elif(self.type == dtype.int):
            assert (self.frac == 0) or not FXP._DBG, 'fractional width must be zero'
            self._to_signed(val)
        elif(self.type == dtype.uint):
            assert (self.frac == 0) or not FXP._DBG, 'fractional width must be zero'
            assert (val >= 0) or not FXP._DBG, 'unsigned number must be non-negative'
            self._to_unsigned(val)
        elif(self.type == dtype.fxp):
            self._to_signed(val)
        elif(self.type == dtype.ufxp):
            assert (val >= 0) or not FXP._DBG, 'unsigned number must be non-negative'
            self._to_unsigned(val)

    def _to_signed(self, val):
        # private method, converts a floating point number to an signed integer value of given width
        half = int(1)<<(self.intg + self.frac)
        full = int(1)<<(self.intg + self.frac + 1)
        if(self.round):
            self._val = ((int(round(val*int(int(1)<<self.frac)))+half)%int(full))-half
        else:
            self._val = ((int(floor(val*int(int(1)<<self.frac)))+half)%int(full))-half

    def _to_unsigned(self, val):
        # private method, converts a floating point number to an unsigned integer value of given width
        full = (int(1)<<(self.intg + self.frac))
        if(self.round):
            self._val = ((int(round(val*int(int(1)<<self.frac))))%int(full))
        else:
            self._val = ((int(floor(val*int(int(1)<<self.frac))))%int(full))

    def convert(self, intg=None, frac=None, type=None, opmode=None, sat=None, round=None, template=None):
        '''
        Public method
        based on the given parameters, changes the object parameters and recalculates the internal value
        can change the internal value because of saturation/overflow, ... .
        '''
        tempval = self.val()
        if(template is not None):
            self._read_template(template)
        if(intg is not None):
            self.intg = intg
        if(frac is not None):
            self.frac = frac
        if(type is not None):
            self.type = type
        if(opmode is not None):
            self.opmode = opmode
        if(sat is not None):
            self.sat = sat
        if(round is not None):
            self.round = round

        self._set_val(tempval)

    def pinf(temp_tuple):
        '''
        Public method, returns highest value of the given bit-width tuple
        for float type the output will be inf
        '''
        return FXP._pinf(temp_tuple[0], temp_tuple[1], temp_tuple[2])

    def ninf(temp_tuple):
        '''
        Public method, returns lowest value of the given bit-width tuple
        for uint and ufxp, the result will be zero
        for float type the output will be -inf
        '''
        return FXP._ninf(temp_tuple[0], temp_tuple[1], temp_tuple[2])

    def _pinf(intg, frac, type):
        '''
        Private method, returns highest value of the given bit-width tuple
        for float type the output will be inf
        '''
        if(type == dtype.float):
            return inf
        else:
            if(intg < 31 and frac < 31):
                return ((int(1)<<(intg+frac))-1)/int(int(1)<<frac)
            else:
                return ((int(1)<<intg)-1)

    def _ninf(intg, frac, type):
        '''
        private method, returns lowest value of the given bit-width tuple
        for uint and ufxp, the result will be zero
        for float type the output will be -inf
        '''
        if(type == dtype.float):
            return -inf
        elif(type == dtype.uint or type == dtype.ufxp):
            return 0
        else:
            if(intg < 31 and frac < 31):
                return -((int(1)<<(intg+frac)))/int(int(1)<<frac)
            else:
                return -((int(1)<<intg))

    def val(self):
        # returns the floating point representation of the object
        if(self.type == dtype.float):
            return self._val
        else:
            return int(self._val)/(int(1)<<self.frac)

    def copy(self,template=None):
        '''
        return a copy of the object when an independent copy of the object is needed. Must be used instead of usual b=a numeric assignment
        if template is given, its parameters will be used to create new object
        '''
        if(template is None):
            return FXP(self.val(), self)
        else:
            return FXP(self.val(), template)

    def to_binary(self):
        '''
            return binary format representation of the object with decimal point
            signed number example  -12.75 with (4,2) bits is S:10011.01
            unsigned number example 10.75 with (4,2) bits is U:1010.11
        '''
        if(self.type == dtype.float):
            s = 'float'
            return s
        elif(self.type == dtype.int or self.type == dtype.fxp):
            s = Bits(int=self._val, length=self.intg+self.frac+1)
            s = s.bin
            return self.type + ':' + s[0:self.intg+1] + '.' + s[self.intg+1:]
        elif(self.type == dtype.uint or self.type == dtype.ufxp):
            s = Bits(int=self._val, length=self.intg+self.frac+1)
            s = s.bin
            return self.type + ':' + s[1:self.intg+1] + '.' + s[self.intg+1:]

    def to_hex(self):
        '''
            return hex format representation of the object without decimal point, extra bits are added to left to make the width multiple of 4
            signed number example  -12.75 with (4,2) bits is S:CD
            unsigned number example 10.75 with (4,2) bits is U:2B
        '''
        if(self.type == dtype.float):
            s = 'float'
            return s
        elif(self.type == dtype.int or self.type == dtype.fxp):
            mul4 = ((self.intg+self.frac+1+3)//4)*4
            s = Bits(int=self._val, length=mul4)
            return self.type + ':' + (s.hex).upper()
        elif(self.type == dtype.uint or self.type == dtype.ufxp):
            mul4 = ((self.intg+self.frac+1+3)//4)*4
            s = Bits(int=self._val, length=mul4)
            return self.type + ':' + (s.hex).upper()

    def __pos__(self):
        # returns a copy of the object
        return self.copy()

    def __neg__(self):
        # returns an object with negative of the value of the object
        return FXP(-self.val(), self)

    def __lt__(self,other):
        # compares an object against another object or number (this obj < other object), (this obj < number)
        if(isinstance(other, FXP)):
            return (self.val() < other.val())
        else:
            return (self.val() < other)

    def __le__(self,other):
        # compares an object against another object or number (this obj <= other object), (this obj <= number)
        if(isinstance(other, FXP)):
            return (self.val() <= other.val())
        else:
            return (self.val() <= other)

    def __gt__(self,other):
        # compares an object against another object or number (this obj > other object), (this obj > number)
        if(isinstance(other, FXP)):
            return (self.val() > other.val())
        else:
            return (self.val() > other)

    def __ge__(self,other):
        # compares an object against another object or number (this obj >= other object), (this obj >= number)
        if(isinstance(other, FXP)):
            return (self.val() >= other.val())
        else:
            return (self.val() >= other)

    def __eq__(self,other):
        # compares an object against another object or number (this obj == other object), (this obj == number)
        if(isinstance(other, FXP)):
            return (self.val() == other.val())
        else:
            return (self.val() == other)

    def __ne__(self,other):
        # compares an object against another object or number (this obj != other object), (this obj != number)
        if(isinstance(other, FXP)):
            return (self.val() != other.val())
        else:
            return (self.val() != other)

    def __str__(self):
        # returns the string format of floating point representation of the object
        if(FXP._DBG):
            # return '(' + str(self.intg) + ', ' + str(self.frac) + ', ' + self.to_binary() + ', ' + self.mode + ') = ' + str(self.val())
            return '[' + str(self.intg) + ', ' + str(self.frac) + ', ' + self.to_binary() + ', ' + self.opmode + ', ' + str(self.sat) + ', ' + str(self.round) + '] = ' + str(self.val())
        else:
            return str(self.val())

    def __repr__(self):
        # returns the string format of floating point representation of the object
        return self.__str__()

    def __abs__(self):
        # returns an object with absolute value of the value of the object
        return FXP(abs(self.val()), self)

    def __add__(self, b):
        # magic function of a + b
        return FXP._add_dispatch(self, b)

    def __radd__(self, b):
        # magic function of b + a
        return FXP._add_dispatch(self, b)

    def __iadd__(self, b):
        # magic function of a += b
        return FXP._add_dispatch(self, b)

    def __sub__(self, b):
        # magic function of a - b
        return FXP._sub_dispatch(self, b)

    def __rsub__(self, b):
        # magic function of b - a
        return -FXP._sub_dispatch(self, b)

    def __isub__(self, b):
        # magic function of a -= b
        return FXP._sub_dispatch(self, b)

    def __mul__(self, b):
        # magic function of a * b
        return FXP._mul_dispatch(self, b)

    def __rmul__(self, b):
        # magic function of b * a
        return FXP._mul_dispatch(self, b)

    def __imul__(self, b):
        # magic function of a *= b
        return FXP._mul_dispatch(self, b)

    def __lshift__(self, other):
        # returns an object with its value is left shifted version of the object
        # c = obj << 3
        return FXP(self.val()*(int(1)<<other), (self.intg+other, max(self.frac-other, 0), self.type, self.opmode, self.sat, self.round))
        # return FXP(self.val()*(int(1)<<other), self)

    def __rshift__(self, other):
        # returns an object with its value is right shifted version of the object (sign bit will fill new bits)
        # c = obj >> 3
        return FXP(self.val()/(int(1)<<other), (min(self.int-other, 0), self.frac+other, self.type, self.opmode, self.sat, self.round))
        # return FXP(self.val()/(int(1)<<other), self)

    def add(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # adds two object a and b and input parameters will be used to set the output parameters, custom output parameter selection
        return FXP._add(a, b, intg, frac, type, opmode, sat, round)

    def sub(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # subtracts two object a and b and input parameters will be used to set the output parameters, custom output parameter selection
        return FXP._sub(a, b, intg, frac, type, opmode, sat, round)

    def mul(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # multiplies two object a and b and input parameters will be used to set the output parameters, custom output parameter selection
        return FXP._mul(a, b, intg, frac, type, opmode, sat, round)

    def _add_dispatch(a, b):
        # returns sum of two object or and object and an integer number (integer number will be converted to same type object with zero fractional width)
        # c = obj + other object
        # c = obj + 3
        if(isinstance(b, FXP)):
            return FXP._add(a, b)
        elif(isinstance(b, int)):
            if(b == 0):
                return a.copy()
            elif(b > 0):
                if(a.type == dtype.float):
                    return FXP._add(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                else:
                    return FXP._add(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.uint, a.opmode, a.sat, a.round)))
            else:
                if(a.type == dtype.float):
                    return FXP._add(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                else:
                    return FXP._add(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.int, a.opmode, a.sat, a.round)))
        else:
            raise Exception("unsupported type ")

    def _sub_dispatch(a, b):
        # returns sum of two object or and object and an integer number (integer number will be converted to same type object with zero fractional width)
        # c = obj - other object
        # c = obj - 3
        if(isinstance(b, FXP)):
            return FXP._sub(a, b)
        elif(isinstance(b, int)):
            if(b == 0):
                return a.copy()
            elif(b > 0):
                if(a.type == dtype.float):
                    return FXP._sub(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                else:
                    return FXP._sub(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.uint, a.opmode, a.sat, a.round)))
            else:
                if(a.type == dtype.float):
                    return FXP._sub(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                else:
                    return FXP._sub(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.int, a.opmode, a.sat, a.round)))
        else:
            raise Exception("unsuppoted type ")

    def _mul_dispatch(a, b):
        # returns product of two object or and object and an integer number (integer number will be converted to same type object with zero fractional width)
        # do not use negative integer operands
        # c = obj * other object
        # c = obj * 3
        if(isinstance(b, FXP)):
            return FXP._mul(a, b)
        elif(isinstance(b, int)):
            if(b == 0):
                return FXP(0, a)
            elif(b > 0):
                if(b & (b-1) == 0):
                    return a.__lshift__(int(log2(b)))
                else:
                    if(a.type == dtype.float):
                        return FXP._mul(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                    else:
                        return FXP._mul(a, FXP(b, (1+int(floor(log2(b))), 0, dtype.uint, a.opmode, a.sat, a.round)))
            else:
                if((-b) & (-b-1) == 0):
                    return -a.__lshift__(int(log2(-b)))
                else:
                    if(a.type == dtype.float):
                        return FXP._mul(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.float, a.opmode, a.sat, a.round)))
                    else:
                        return FXP._mul(a, FXP(b, (1+int(floor(log2(-b))), 0, dtype.int, a.opmode, a.sat, a.round)))
        else:
            raise Exception("unsupported type")

    def _add(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # private method, implements the addition operation
        if(opmode is None):
            assert(a.opmode == b.opmode) or not FXP._DBG, 'operands must have the same opmode'
            opmode = a.opmode
        if(sat is None):
            assert(a.sat == b.sat) or not FXP._DBG, 'operands must have the same saturation mode'
            sat = a.sat
        if(round is None):
            assert(a.round == b.round) or not FXP._DBG, 'operands must have the same rounding mode'
            round = a.round

        assert((a.type == dtype.float and b.type == dtype.float) or (a.type != dtype.float and b.type != dtype.float)) or not FXP._DBG, 'Float - fixedpoint operation is not allowed'
        temp = (a.type, b.type)
        if(type is None):
            if(temp == (dtype.float, dtype.float)):
                type    = dtype.float
                tempval = a._val + b._val
            else:
                if(temp == (dtype.uint, dtype.uint)):
                    type = dtype.uint
                elif(temp == (dtype.uint, dtype.int) or temp == (dtype.int, dtype.uint)):
                    type = dtype.int
                elif(temp == (dtype.uint, dtype.ufxp) or temp == (dtype.ufxp, dtype.uint)):
                    type = dtype.ufxp
                else:
                    type = dtype.fxp
                if(a.frac >= b.frac):
                    tempval = a._val + (int(b._val) << (a.frac - b.frac))
                    tempval = tempval / int(2**a.frac)
                else:
                    tempval = b._val + (int(a._val) << (b.frac - a.frac))
                    tempval = tempval / int(2**b.frac)

        if(opmode == modes.FULL):
            intg = max(a.intg, b.intg) + 1
            frac = max(a.frac, b.frac)
        elif(opmode == modes.FIXEDFRAC):
            intg = max(a.intg, b.intg) + 1
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.FIXEDWIDTH):
            intg = max(a.intg, b.intg)
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.MANUAL):
            opmode = None
            pass

        return FXP(tempval,(intg, frac, type, opmode, sat, round))

    def _sub(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # private method, implements the addition operation
        if(opmode is None):
            assert(a.opmode == b.opmode) or not FXP._DBG, 'operands must have the same opmode'
            opmode = a.opmode
        if(sat is None):
            assert(a.sat == b.sat) or not FXP._DBG, 'operands must have the same saturation mode'
            sat = a.sat
        if(round is None):
            assert(a.round == b.round) or not FXP._DBG, 'operands must have the same rounding mode'
            round = a.round

        assert((a.type == dtype.float and b.type == dtype.float) or (a.type != dtype.float and b.type != dtype.float)) or not FXP._DBG, 'Float - fixedpoint operation is not allowed'
        temp = (a.type, b.type)
        if(type is None):
            if(temp == (dtype.float, dtype.float)):
                type    = dtype.float
                tempval = a._val - b._val
            else:
                if(temp == (dtype.uint, dtype.uint)):
                    type = dtype.uint
                elif(temp == (dtype.uint, dtype.int) or temp == (dtype.int, dtype.uint)):
                    type = dtype.int
                elif(temp == (dtype.uint, dtype.ufxp) or temp == (dtype.ufxp, dtype.uint)):
                    type = dtype.ufxp
                else:
                    type = dtype.fxp
                if(a.frac >= b.frac):
                    tempval = a._val - (int(b._val) << (a.frac - b.frac))
                    tempval = tempval / int(2**a.frac)
                else:
                    tempval = -b._val + (int(a._val) << (b.frac - a.frac))
                    tempval = tempval / int(2**b.frac)

        if(opmode == modes.FULL):
            intg = max(a.intg, b.intg) + 1
            frac = max(a.frac, b.frac)
        elif(opmode == modes.FIXEDFRAC):
            intg = max(a.intg, b.intg) + 1
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.FIXEDWIDTH):
            intg = max(a.intg, b.intg)
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.MANUAL):
            opmode = None
            pass

        return FXP(tempval,(intg, frac, type, opmode, sat, round))

    def _mul(a, b, intg=0, frac=0, type=None, opmode=None, sat=None, round=None):
        # private method, implements the multiplication operation
        if(opmode is None):
            assert(a.opmode == b.opmode) or not FXP._DBG, 'operands must have the same opmode'
            opmode = a.opmode
        if(sat is None):
            assert(a.sat == b.sat) or not FXP._DBG, 'operands must have the same saturation mode'
            sat = a.sat
        if(round is None):
            assert(a.round == b.round) or not FXP._DBG, 'operands must have the same rounding mode'
            round = a.round

        assert((a.type == dtype.float and b.type == dtype.float) or (a.type != dtype.float and b.type != dtype.float)) or not FXP._DBG, 'Float - fixedpoint operation is not allowed'
        temp = (a.type, b.type)
        if(type is None):
            if(temp == (dtype.float, dtype.float)):
                type    = dtype.float
                tempval = a._val * b._val
            else:
                if(temp == (dtype.uint, dtype.uint)):
                    type = dtype.uint
                elif(temp == (dtype.uint, dtype.int) or temp == (dtype.int, dtype.uint)):
                    type = dtype.int
                elif(temp == (dtype.uint, dtype.ufxp) or temp == (dtype.ufxp, dtype.uint)):
                    type = dtype.ufxp
                else:
                    type = dtype.fxp
                tempval = a._val * b._val
                tempval = tempval / int(2**(a.frac+b.frac))

        if(opmode == modes.FULL):
            intg = a.intg + b.intg
            frac = a.frac + b.frac
        elif(opmode == modes.FIXEDFRAC):
            intg = a.intg + b.intg
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.FIXEDWIDTH):
            intg = max(a.intg, b.intg)
            if((a.type == dtype.uint or a.type == dtype.int) and (b.type == dtype.ufxp or b.type == dtype.fxp)):
                frac = b.frac
            elif((b.type == dtype.uint or b.type == dtype.int) and (a.type == dtype.ufxp or a.type == dtype.fxp)):
                frac = a.frac
            else:
                frac = min(a.frac, b.frac)
        elif(opmode == modes.MANUAL):
            opmode = None
            pass

        return FXP(tempval,(intg, frac, type, opmode, sat, round))

    def debug(enable=None):
        # enables/disables debug mode. warnings and assertions will be suppressed when debug is False
        if(isinstance(enable,bool)):
            FXP._DBG = enable
