//   Copyright:
//       Copyright 2017 Ahmad RezazadehReyhani
//
//       Licensed under the Apache License, Version 2.0 (the "License");
//       you may not use this file except in compliance with the License.
//       You may obtain a copy of the License at
//
//          http://WWW.apache.org/licenses/LICENSE-2.0
//
//       Unless required by applicable law or agreed to in writing, software
//       distributed under the License is distributed on an "AS IS" BASIS,
//       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//       See the License for the specific language governing permissions and
//       limitations under the License.
//
//   Acknowledgment:
//       Grateful appreciation to the Farhang Wireless Inc. for their support and generously funding the implementation of this library.
//       http://farhangwireless.com/

#include <iostream>
#include <sstream>
#include <stdint.h>
#include <cassert>
#include <cmath>

#define _DEBUG

#define fastfloor(x) ((double)(int64_t)x - (x < (double)(int64_t)x))
#define fastceil(x)  ((double)(int64_t)x + (x > (double)(int64_t)x))
#define fastmax(a,b) ((a)>(b)?(a):(b))
#define fastmin(a,b) ((a)<(b)?(a):(b))

using namespace std;

// -----------------------------------
template < typename T >
string to_str(const T& n)
{
    ostringstream stm;
    stm.precision(15);
    stm << n;
    stm.precision(15);
    return stm.str();
}
// -----------------------------------
string int2bin(int64_t val, int n)
{
    string binary = "";
    int64_t mask = 1;
    for(int i = 0; i < n; i++)
    {
        if((mask&val) >= 1)
            binary = "1"+binary;
        else
            binary = "0"+binary;
        mask <<= 1;
    }
    return binary;
}
// -----------------------------------
double inf = INFINITY;
enum dtype {d_INT, d_UINT, d_FXP, d_UFXP, d_FLOAT};
/*
    Fixedpoint variable types
    d_INT     : signed integer variable
    d_UINT    : unsigned integer variable
    d_FXP     : signed fractional variable
    d_UFXP    : unsigned fractional variable
    d_FLOAT   : floating point variable
*/
enum modes {FULL, FIXEDFRAC, FIXEDWIDTH, MANUAL};
/*
    arithmetic operation modes
    FULL        : output width is inferred from operands to keep exact operation results
    FIXEDFRAC   : output integer width grows to fit the results, but fractional width keeps track of significant bits
    FIXEDWIDTH  : output integer width is equal to the maximum of input integer widths, and output fractional width is the minimum of input fractional widths
    MANUAL      : output widths will be given by user
*/
// -----------------------------------
class tuple;
class tuple
{
    public:
    int     intg;
    int     frac;
    dtype   type;
    modes   opmode;
    bool    sat;
    bool    rounding;

    tuple(int intg, int frac, dtype type, modes opmode, bool sat, bool rounding)
    {
        this->intg      = intg;
        this->frac      = frac;
        this->type      = type;
        this->opmode    = opmode;
        this->sat       = sat;
        this->rounding  = rounding;
    }
    tuple(void)
    {}
};
// -----------------------------------
class FXP
/*
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
            inf   : actual value will be maximum possible value of given bit width
            -inf  : actual value will be minimum possible value of given bit width

    Operands must have same opmode, sat and round settings.
    Fractional width of int and uint type must be zero.
    value of uint and ufxp object must be non-negative.
*/
{
public:

    double  _val;
    int     intg;
    int     frac;
    dtype   type;
    modes   opmode;
    bool    sat;
    bool    rounding;

    double  pinf;
    double  ninf;
    double shift;
    int64_t full;
    int64_t half;

    FXP(){}
    /*
    public method
    Class constructor
    val is a floating point value
    template is a tuple or another FXP object
     */
    template <typename TYPE>
    FXP(double val, TYPE templ)
    {
        _read_template(templ);
        _set_bounds();
        _set_val(val);
    }

    // Extracts object parameters from the given template
    template <typename TYPE>
    void _read_template(TYPE templ)
    {
        this->intg      = templ.intg;
        this->frac      = templ.frac;
        this->type      = templ.type;
        this->opmode    = templ.opmode;
        this->sat       = templ.sat;
        this->rounding  = templ.rounding;
    }

    void _set_bounds(void)
    {
        this->shift = double(((int64_t)1) << this->frac);
        // signed
        if((this->type == d_UINT) | (this->type == d_UFXP))
        {
            this->full = ((int64_t)1) << (this->intg + this->frac);
            this->half = 0;
        }
        else
        {
            this->full = ((int64_t)1) << (this->intg + this->frac + 1);
            this->half = ((int64_t)1) << (this->intg + this->frac);
        }

        if(this->type == d_FLOAT)
        {
            this->pinf  =  inf;
            this->ninf  = -inf;
        }
        else
        {
            if( (this->intg < 31) & (this->frac < 31))
            {
                this->pinf =  ((double)( (((int64_t)1) << (this->intg+this->frac) ) - 1 )) / this->shift;
                this->ninf = ((this->type == d_UINT) | (this->type == d_UFXP)) ? 0 : -((double)(((int64_t)1) << (this->intg+this->frac) )) / this->shift;
            }
            else
            {
                this->pinf =  (double)(( ((int64_t)1) << this->intg)-1);
                this->ninf = ((this->type == d_UINT) | (this->type == d_UFXP)) ? 0 : -(double)( ((int64_t)1) << this->intg);
            }
        }
    }

    /*
    sets the internal value of the object based on the given parameters
    saturation/rounding/with set/change is applied in this method
    */
    void _set_val(double val)
    {
        #ifdef _DEBUG
	    double tempval = val;
            assert((this->intg + this->frac) < 63);
        #endif

        if(val == inf)
            val = this->pinf;
        if(val == -inf)
            val = this->ninf;

        if(this->sat)
        {
            if(val > this->pinf)
            {
                #ifdef _DEBUG_FULL
                    cout << "saturation !" << this->intg << ", " << this->frac << ", " << this->type << ", " << pinf << ", " << val << "\n";
                #endif
                val = this->pinf;
            }
            if(val < this->ninf)
            {
                #ifdef _DEBUG_FULL
                    cout << "saturation !" << this->intg << ", " << this->frac << ", " << this->type << ", " << ninf << ", " << val << "\n";
                #endif
                val = ninf;
            }
        }
        else
        {
            if(val > this->pinf)
            {
                #ifdef _DEBUG_FULL
                    cout << "overflow !" << this->intg << ", " << this->frac << ", " << this->type << ", " << pinf << ", " << val << "\n";
                #endif
            }
            if(val < this->ninf)
            {
                #ifdef _DEBUG_FULL
                    cout << "overflow !" << this->intg << ", " << this->frac << ", " << this->type << ", " << pinf << ", " << val << "\n";
                #endif
            }
        }
        if(this->type == d_FLOAT)
            this->_val = val;
        else if(this->type == d_INT)
        {
            #ifdef _DEBUG
                assert((this->frac == 0));
            #endif
            _to_signed(val);
        }
        else if(this->type == d_UINT)
        {
            #ifdef _DEBUG
                assert((this->frac == 0));
                assert((val >= 0));
            #endif
            _to_unsigned(val);
        }
        else if(this->type == d_FXP)
            _to_signed(val);
        else if(this->type == d_UFXP)
        {
            #ifdef _DEBUG
                assert((val >= 0));
            #endif
            _to_unsigned(val);
        }
        #ifdef _DEBUG
            if(tempval * this->_val < 0)
            cout << "sign change from " << tempval << " to " << this->_val << "\n";
            assert(tempval * this->_val >= 0);
        #endif
    }

    //# private method, converts a floating point number to an signed integer value of given width
    void _to_signed(double val)
    {
        double  temp = val * this->shift;
        if(this->rounding)
            temp = round(temp);
        else
            temp = fastfloor(temp);
        int64_t tempint = (((int64_t)temp + this->half) % this->full);
        if(tempint < 0)
            tempint += this->full;
        this->_val = double(tempint - this->half);
    }

    // private method, converts a floating point number to an unsigned integer value of given width
    void _to_unsigned(double val)
    {
        double  temp = val * this->shift;
        if(this->rounding)
            temp = round(temp);
        else
            temp = fastfloor(temp);
        int64_t tempint = (int64_t)temp  % this->full;
        if(tempint < 0)
            tempint += this->full;
        this->_val = double(tempint);
    }

    // returns the floating point representation of the object
    double val()
    {
        if(this->type == d_FLOAT)
            return this->_val;
        else
            return this->_val / this->shift;
    }

    /*
    based on the given parameters, changes the object parameters and recalculates the internal value
    can change the internal value because of saturation/overflow, ... .
    */
    void convert(int intg , int frac, dtype type)
    {
        double tempval = this->val();
        this->intg = intg;
        this->frac = frac;
        this->type = type;
        _set_bounds();
        _set_val(tempval);
    }
    void convert(modes opmode)
    {
        this->opmode = opmode;
    }
    void convert(bool sat, bool rounding )
    {
        this->sat = sat;
        this->rounding = rounding;
    }
    void convert(int intg , int frac, dtype type, modes opmode, bool sat, bool rounding)
    {
        double tempval = this->val();
        this->intg = intg;
        this->frac = frac;
        this->type = type;
        this->opmode = opmode;
        this->sat = sat;
        this->rounding = rounding;
        _set_bounds();
        _set_val(tempval);
    }
    template <typename TYPE>
    void convert(TYPE templ)
    {
        double tempval = this->val();
        _read_template(templ);
        _set_bounds();
        _set_val(tempval);
    }

    /*
    return a copy of the object when an independent copy of the object is needed. Must be used instead of usual b=a numeric assignment
    if template is given, its parameters will be used to create new object
    */
    FXP copy()
    {
        return FXP(this->val(), *this);
    }

    template <typename TYPE>
    FXP copy(TYPE templ)
    {
        return FXP(this->val(), templ);
    }

    /*
    return binary format representation of the object with decimal point
    signed number example  -12.75 with (4,2) bits is S:10011.01
    unsigned number example 10.75 with (4,2) bits is U:1010.11
    */
    string to_binary()
    {
        string s;
        if(this->type == d_FLOAT)
        {
            s = "float";
            return s;
        }
        else if((this->type == d_INT) | (this->type == d_FXP))
        {
            s = int2bin((int64_t)this->_val, this->intg+this->frac+1);
            return s.substr(0,this->intg+1) + "." + s.substr(this->intg+1,this->frac);
        }
        else// if((a.type == d_UINT) | (a.type == d_UFXP))
        {
            s = int2bin((int64_t)this->_val, this->intg+this->frac+1);
            return s.substr(1,this->intg) + "." + s.substr(this->intg+1,this->frac);;
        }
    }

    string str()
    {
        return "[" + to_str(this->intg) + ", " + to_str(this->frac) + ", " + this->to_binary()  + ", " + to_str(this->type) + ", " + to_str(this->opmode) + ", " + to_str(this->sat) + ", " + to_str(this->rounding) + "] = " + to_str(this->val());
    }

}; // FXP
// -----------------------------------
// operator overloading
// -----------------------------------
FXP operator+(FXP a)
{
    return a.copy();
}
FXP operator-(FXP a)
{
    return FXP(-a.val(),a);
}
// -----------------------------------
bool operator<(FXP a, FXP b)
{
    return (a.val() < b.val());
}
template <typename TYPE>
bool operator<(FXP a, TYPE b)
{
    return (a.val() < b);
}
// -----------------------------------
bool operator<=(FXP a, FXP b)
{
    return (a.val() <= b.val());
}
template <typename TYPE>
bool operator<=(FXP a, TYPE b)
{
    return (a.val() <= b);
}
// -----------------------------------
bool operator>(FXP a, FXP b)
{
    return (a.val() > b.val());
}
template <typename TYPE>
bool operator>(FXP a, TYPE b)
{
    return (a.val() > b);
}
// -----------------------------------
bool operator>=(FXP a, FXP b)
{
    return (a.val() >= b.val());
}
template <typename TYPE>
bool operator>=(FXP a, TYPE b)
{
    return (a.val() >= b);
}// -----------------------------------
bool operator==(FXP a, FXP b)
{
    return (a.val() == b.val());
}
template <typename TYPE>
bool operator==(FXP a, TYPE b)
{
    return (a.val() == b);
}
// -----------------------------------
bool operator!=(FXP a, FXP b)
{
    return (a.val() != b.val());
}
template <typename TYPE>
bool operator!=(FXP a, TYPE b)
{
    return (a.val() != b);
}
// -----------------------------------
FXP operator>>(FXP a, int b)
{
    return FXP(a.val()/(1<<b), tuple((int)fastmin(a.intg-b, 0), a.frac+b, a.type, a.opmode, a.sat, a.rounding));
}
// -----------------------------------
FXP operator<<(FXP a, int b)
{
    return FXP(a.val()*(1<<b), tuple(a.intg+b, (int)fastmax(a.frac-b, 0), a.type, a.opmode, a.sat, a.rounding));
}
// -----------------------------------
FXP abs(FXP a)
{
    return FXP(fabs(a.val()),a);
}
// -----------------------------------
FXP max(FXP a, FXP b)
{
    if(a > b)
        return a.copy();
    else
        return b.copy();
}
// -----------------------------------
FXP min(FXP a, FXP b)
{
    if(a < b)
        return a.copy();
    else
        return b.copy();
}
// -----------------------------------
/*
returns sum of two object or and object and an integer number (integer number will be converted to same type object with zero fractional width)
c = obj + other object
c = obj + 3
*/
FXP _add(FXP a, FXP b, modes opmode, bool sat, bool rounding)
{
    dtype type;
    double tempval=0;
    int intg = 0;
    int frac = 0;
    if((a.type == d_FLOAT) & (b.type == d_FLOAT))
    {
        type    = d_FLOAT;
        tempval = a._val + b._val;
    }
    else
    {
        if((a.type == d_UINT) & (b.type == d_UINT))
            type = d_UINT;
        else if(((a.type == d_UINT) & (b.type == d_INT)) | ((a.type == d_INT) & (b.type == d_UINT)))
            type = d_INT;
        else if(((a.type == d_UINT) & (b.type == d_UFXP)) | ((a.type == d_UFXP) & (b.type == d_UINT)))
            type = d_UFXP;
        else
            type = d_FXP;
        if(a.frac >= b.frac)
        {
            tempval = a._val + double(((int64_t)b._val) << (a.frac - b.frac));
            tempval = tempval /a.shift;
        }
        else
        {
            tempval = b._val + double(((int64_t)a._val) << (b.frac - a.frac));
            tempval = tempval /b.shift;
        }
    }
    if(opmode == FULL)
    {
        intg = fastmax(a.intg, b.intg) + 1;
        frac = fastmax(a.frac, b.frac);
    }
    else if(opmode == FIXEDFRAC)
    {
        intg = fastmax(a.intg, b.intg) + 1;
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }
    else if(opmode == FIXEDWIDTH)
    {
        intg = (int)fastmax(a.intg, b.intg);
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }

    return FXP(tempval,tuple(intg, frac, type, opmode, sat, rounding));
}
FXP _add(FXP a, FXP b)
{
    #ifdef _DEBUG
        assert((a.opmode   == b.opmode));
        assert((a.sat      == b.sat   ));
        assert((a.rounding == b.rounding));
        assert((((a.type == d_FLOAT) & (b.type == d_FLOAT)) | ((a.type != d_FLOAT) & (b.type != d_FLOAT))));
    #endif
    return _add(a, b, a.opmode, a.sat, a.rounding);
}
// -----------------------------------
FXP _sub(FXP a, FXP b, modes opmode, bool sat, bool rounding)
{
    dtype type;
    double tempval=0;
    int intg = 0;
    int frac = 0;
    if((a.type == d_FLOAT) & (b.type == d_FLOAT))
    {
        type    = d_FLOAT;
        tempval = a._val - b._val;
    }
    else
    {
        if((a.type == d_UINT) & (b.type == d_UINT))
            type = d_INT;
        else if(((a.type == d_UINT) & (b.type == d_INT)) | ((a.type == d_INT) & (b.type == d_UINT)))
            type = d_INT;
        else if(((a.type == d_UINT) & (b.type == d_UFXP)) | ((a.type == d_UFXP) & (b.type == d_UINT)))
            type = d_FXP;
        else
            type = d_FXP;
        if(a.frac >= b.frac)
        {
            tempval = a._val - double(((int64_t)b._val) << (a.frac - b.frac));
            tempval = tempval /a.shift;
        }
        else
        {
            tempval = -b._val + double(((int64_t)a._val) << (b.frac - a.frac));
            tempval = tempval / b.shift;
        }
    }
    if(opmode == FULL)
    {
        intg = fastmax(a.intg, b.intg) + 1;
        frac = fastmax(a.frac, b.frac);
    }
    else if(opmode == FIXEDFRAC)
    {
        intg = fastmax(a.intg, b.intg) + 1;
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }
    else if(opmode == FIXEDWIDTH)
    {
        intg = fastmax(a.intg, b.intg);
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }

    return FXP(tempval,tuple(intg, frac, type, opmode, sat, rounding));
}
FXP _sub(FXP a, FXP b)
{
    #ifdef _DEBUG
        assert((a.opmode   == b.opmode));
        assert((a.sat      == b.sat   ));
        assert((a.rounding == b.rounding));
        assert((((a.type == d_FLOAT) & (b.type == d_FLOAT)) | ((a.type != d_FLOAT) & (b.type != d_FLOAT))));
    #endif
    return _sub(a, b, a.opmode, a.sat, a.rounding);
}
// -----------------------------------
/*
returns product of two object or and object and an integer number (integer number will be converted to same type object with zero fractional width)
do not use negative integer operands
c = obj * other object
c = obj * 3
*/
FXP _mul(FXP a, FXP b, modes opmode, bool sat, bool rounding)
{
    dtype type;
    double tempval=0;
    int intg = 0;
    int frac = 0;
    if((a.type == d_FLOAT) & (b.type == d_FLOAT))
    {
        type    = d_FLOAT;
        tempval = a._val * b._val;
    }
    else
    {
        if((a.type == d_UINT) & (b.type == d_UINT))
            type = d_UINT;
        else if(((a.type == d_UINT) & (b.type == d_INT)) | ((a.type == d_INT) & (b.type == d_UINT)))
            type = d_INT;
        else if(((a.type == d_UINT) & (b.type == d_UFXP)) | ((a.type == d_UFXP) & (b.type == d_UINT)))
            type = d_UFXP;
        else
            type = d_FXP;
        tempval = a._val * b._val;
        tempval = tempval / double(((int64_t)1) << (a.frac+b.frac));
    }
    if(opmode == FULL)
    {
        intg = a.intg + b.intg;
        frac = a.frac + b.frac;
    }
    else if(opmode == FIXEDFRAC)
    {
        intg = a.intg + b.intg;
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }
    else if(opmode == FIXEDWIDTH)
    {
        intg = fastmax(a.intg, b.intg);
        if     (((a.type == d_UINT) | (a.type == d_INT)) & ((b.type == d_UFXP) | (b.type == d_FXP)))
            frac = b.frac;
        else if(((b.type == d_UINT) | (b.type == d_INT)) & ((a.type == d_UFXP) | (a.type == d_FXP)))
            frac = a.frac;
        else
            frac = fastmin(a.frac, b.frac);
    }

    return FXP(tempval,tuple(intg, frac, type, opmode, sat, rounding));
}
FXP _mul(FXP a, FXP b)
{
    #ifdef _DEBUG
        assert((a.opmode   == b.opmode));
        assert((a.sat      == b.sat   ));
        assert((a.rounding == b.rounding));
        assert((((a.type == d_FLOAT) & (b.type == d_FLOAT)) | ((a.type != d_FLOAT) & (b.type != d_FLOAT))));
    #endif
    return _mul(a, b, a.opmode, a.sat, a.rounding);
}
// -----------------------------------
FXP operator+(FXP a, FXP b)
{
    return _add(a, b);
}
FXP operator+(FXP a, int b)
{
    if(b == 0)
        return a.copy();
    else
        if(b > 0)
            if(a.type == d_FLOAT)
                return _add(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
            else
                return _add(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_UINT,  a.opmode, a.sat, a.rounding)));
        else
            if(a.type == d_FLOAT)
                return _add(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
            else
                return _add(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_INT  , a.opmode, a.sat, a.rounding)));
}
FXP operator+(int a, FXP b)
{
    return b + a;
}
// -----------------------------------
FXP operator-(FXP a, FXP b)
{
    return _sub(a, b);
}
FXP operator-(FXP a, int b)
{
    if(b == 0)
        return a.copy();
    else
        if(b > 0)
            if(a.type == d_FLOAT)
                return _sub(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
            else
                return _sub(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_UINT,  a.opmode, a.sat, a.rounding)));
        else
            if(a.type == d_FLOAT)
                return _sub(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
            else
                return _sub(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_INT  , a.opmode, a.sat, a.rounding)));
}
FXP operator-(int a, FXP b)
{
    return -b + a;
}
// -----------------------------------
FXP operator*(FXP a, FXP b)
{
    return _mul(a,b);
}
FXP operator*(FXP a, int b)
{
    if(b == 0)
        return FXP(0, a);
    else
        if(b > 0)
            if((b & (b-1)) == 0)
                return a << (int(log2(b)));
            else
                if(a.type == d_FLOAT)
                    return _mul(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
                else
                    return _mul(a, FXP(b, tuple(1+int(fastfloor(log2(b))), 0, d_UINT , a.opmode, a.sat, a.rounding)));
        else
            if(((-b) & (-b-1)) == 0)
                return a << (int(log2(-b)));
            else
                if(a.type == d_FLOAT)
                    return _mul(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
                else
                    return _mul(a, FXP(b, tuple(1+int(fastfloor(log2(-b))), 0, d_FLOAT, a.opmode, a.sat, a.rounding)));
}
FXP operator*(int a, FXP b)
{
    return b * a;
}
// -----------------------------------
std::ostream& operator<< (std::ostream & out, FXP a)
{
    out << a.str();
    return out;
}
// -----------------------------------
