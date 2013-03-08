Configurable algorithms: conditionals or function pointers?
===========================================================

So you've got a model with many optional parts, represented as several subroutines with the same 
signatures operating in some well-defined order.  What's the best way to capture the model 
configuration both for efficiency and extensibility?  The approaches that come to mind are:

1. Conditional compilation,
2. A large subroutine/program that knows about every subroutine and makes conditional calls,
3. A sequence of procedure pointers.

Conditional compilation is obviously going to result in the smallest, fastest machine code, however 
it comes at the cost of runtime configuration, making the model a lot less useful as a library for 
another project.

Conditionally calling each subroutine allows configuration at runtime, but the conditionals add 
overhead to the calls.  Also, it requires a master subroutine which knows about all subroutines that 
might every be called, which might lead to a code organisation headache.

Using procedure pointers gives complete configuration ability.  Effectively the model configuration 
is converted to a sequence of subroutines to call.  Any subroutine with a compatible signature can 
be called, which even allows processing steps written in other languages if ISO C bindings are used 
throughout.  Dealing with subroutines as rearrangeable values can even allow for more advanced 
handling, for example automatically resolving execution order dependencies based on metadata, 
removing the need for a "master subroutine".

Obviously, each extra bit of abstraction adds overhead.  The question is, how much?


Testing
-------

The different methods are all compared with the same test: create an array of 10,000,000 random 
numbers, and for each one make 5 procedure calls using the method being tested.  The subroutines do 
some very basic numerical work; the idea is to somewhat amplify the effect that the calling 
mechanism has compared to a much coarser-grained model.

The same procedures and the same values are used each time to eliminate them as sources of 
variation.  Only the processing loop is timed, since the setup is a one-time cost and would only 
serve to hide the magnitude of variation in the results.

All of the configuration-based methods expect the configuration string "5 4 3 2 1" on standard 
input; this is to limit any assumptions that an optimiser might make about a constant configuration.


Results
-------

Each variant was compiled and run, once with "safe" compiler flags and once with "optimised" flags.  
These are the results I got with GNU Fortran 4.7.2, ordered fastest to slowest.

========================  ==================  ===================================================
Method                    ``-fcheck=all``     ``-O3 -march=native -ffast-math -funroll-loops``
========================  ==================  ===================================================
``normal_calls.f90``      1.031588288         0.731172012
``optional_calls.f90``    1.033456319         0.740827716
``linkedlist_calls.f90``  1.042454953         0.823142803
``array_calls.f90``       1.101201001         0.836708802
========================  ==================  ===================================================

