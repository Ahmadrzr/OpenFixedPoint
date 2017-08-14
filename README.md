# Welcome to OpenFixedPoint Library!

OpenFixedPoint Library is an open source C++/Python library for bit-accurate simulation/implementations of DSP algorithms, Software Defined Radios or similar systems.

# Features
	- fixedpoint variable class with per variable properties
	- support for C++ and Python3
	- support for float, fixedpoint, unsigned fixedpoint, integer, unsigned integer
	- support for up to 52-bit fixedpoint variables
	- support for fixedpoint/floating point simulation
	- support for rounding/truncation
	- support for saturation/wrap around
	- support for full precision, fixed width, fixed fractional, and manual operation output bit-width
	- support for operator overloading for +, -, * operators
	- support for integer-fixedpoint and unsigned integer-fixedpoint operation
	- support for debug/release mode

# Requirements
	- fixedpoint.py
		- Python3
		- numpy
		- bitstring
	- fixedpoint.cpp
		- C++ standard libraries

# Build Instruction
	- fixedpoint.cpp
		- use src/Makefile

# Test
	- use test/test_fixedpoint.sh script to run example use of fixedpointlib C++ and Python libraries
	- see src/test_fixedpointlib.cpp for example use of fixedpointlib.cpp
	- see src/test_fixedpointlib.py for example use of fixedpointlib.py

# Target Platforms
	- Linux
	- Windows

# Copyright
	Copyright 2017 Ahmad RezazadehReyhani

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	   http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.

# Acknowledgment
	Grateful appreciation to the Farhang Wireless Inc. for their support and generously funding the implementation of this library.
  (http://farhangwireless.com)
