#	Copyright:
#		Copyright 2017 Ahmad RezazadehReyhani
#
#		Licensed under the Apache License, Version 2.0 (the "License");
#		you may not use this file except in compliance with the License.
#		You may obtain a copy of the License at
#
#		   http://www.apache.org/licenses/LICENSE-2.0
#
#		Unless required by applicable law or agreed to in writing, software
#		distributed under the License is distributed on an "AS IS" BASIS,
#		WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#		See the License for the specific language governing permissions and
#		limitations under the License.
#
#   Acknowledgment:
#		Grateful appreciation to the Farhang Wireless Inc. for their support and generously funding the implementation of this library.
#   	http://farhangwireless.com/

all: test_fixedpointlib.out

test_fixedpointlib.out: fixedpointlib.cpp test_fixedpointlib.cpp
	g++ -O3 -Wall -Wconversion -std=c++03 -march=native -o test_fixedpointlib.out test_fixedpointlib.cpp
clean:
	rm test_fixedpointlib.out
