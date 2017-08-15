//	Copyright:
//		Copyright 2017 Ahmad RezazadehReyhani
//
//		Licensed under the Apache License, Version 2.0 (the "License");
//		you may not use this file except in compliance with the License.
//		You may obtain a copy of the License at
//
//		   http://www.apache.org/licenses/LICENSE-2.0
//
//		Unless required by applicable law or agreed to in writing, software
//		distributed under the License is distributed on an "AS IS" BASIS,
//		WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//		See the License for the specific language governing permissions and
//		limitations under the License.
//
//   Acknowledgment:
//		Grateful appreciation to the Farhang Wireless Inc. for their support and generously funding the implementation of this library.
//   	http://farhangwireless.com/

#include "fixedpointlib.cpp"

int main()
{
    double number1 = -11.123456789;
    double number2 = 39.987654321;

    FXP var_1  = FXP(number1, tuple(30,10,d_FXP, FULL,false,false));
    FXP var_2  = FXP(number1, tuple(10,10,d_FXP, FULL,false,false));
    FXP var_3  = FXP(number1, tuple(9,5,d_FXP, FIXEDFRAC,false,false));
    FXP var_4  = FXP(number2, tuple(7,1,d_FXP, FIXEDFRAC,false,false));
    FXP var_5  = FXP(number2, var_4);
    FXP int_1  = FXP(-3, tuple(3,0,d_INT, FIXEDFRAC,false,false));
    FXP uint_1 = FXP(+3, tuple(3,0,d_UINT, FIXEDFRAC,false,false));
    FXP var_inf= FXP(inf, tuple(7,1,d_FLOAT, FIXEDFRAC,false,false));

    cout << " var_1   = " << var_1 << "\n";
    cout << " var_2   = " << var_2 << "\n";
    cout << " var_3   = " << var_3 << "\n";
    cout << " var_4   = " << var_4 << "\n";
    cout << " var_5   = " << var_5 << "\n";
    cout << " int_1   = " << int_1 << "\n";
    cout << " uint_1  = " << uint_1 << "\n";
    cout << " var_inf = " << var_inf << "\n";

    cout << "\n";

    cout << " var_1 + var_2 = " << var_1 + var_2 << " \n";
    cout << " var_3 + var_4 = " << var_3 + var_4 << " \n";
    cout << " var_3 - var_4 = " << var_3 - var_4 << " \n";
    cout << " var_3 * var_4 = " << var_3 * var_4 << " \n";

    cout << "\n";

    cout << " var_3 + 2 = " << var_3 + 2 << " \n";
    cout << " 3 - var_3 = " << 3 - var_3 << " \n";
    cout << " 5 * var_3 = " << 5 * var_3 << " \n";

    return 0;
}

