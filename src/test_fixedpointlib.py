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


from fixedpointlib import FXP, dtype, modes

FXP.debug(True)

number1 = -11.123456789
number2 = 39.987654321

var_1  = FXP(number1, (30,10,dtype.fxp, modes.FULL,False,False))
var_2  = FXP(number1, (10,10,dtype.fxp, modes.FULL,False,False))
var_3  = FXP(number1, (9,5,dtype.fxp, modes.FIXEDFRAC,False,False))
var_4  = FXP(number2, (7,1,dtype.fxp, modes.FIXEDFRAC,False,False))
var_5  = FXP(number2, var_4)
int_1  = FXP(-3, (3,0,dtype.int, modes.FIXEDFRAC,False,False))
uint_1 = FXP(+3, (3,0,dtype.uint, modes.FIXEDFRAC,False,False))
var_inf= FXP('inf', (7,1,dtype.float, modes.FIXEDFRAC,False,False))

print(" var_1   = ",end='') ; print( var_1)
print(" var_2   = ",end='') ; print( var_2)
print(" var_3   = ",end='') ; print( var_3)
print(" var_4   = ",end='') ; print( var_4)
print(" var_5   = ",end='') ; print( var_5)
print(" int_1   = ",end='') ; print( int_1)
print(" uint_1  = ",end='') ; print( uint_1)
print(" var_inf = ",end='') ; print( var_inf)

print("\n")

print(" var_1 + var_2 = ",end='');print( var_1 + var_2 )
print(" var_3 + var_4 = ",end='');print( var_3 + var_4 )
print(" var_3 - var_4 = ",end='');print( var_3 - var_4 )
print(" var_3 * var_4 = ",end='');print( var_3 * var_4 )

print("\n")

print(" var_3 + 2 = ",end='');print( var_3 + 2 )
print(" 3 - var_3 = ",end='');print( 3 - var_3 )
print(" 5 * var_3 = ",end='');print( 5 * var_3 )
