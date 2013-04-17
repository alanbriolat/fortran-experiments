module funcpointerinterop

    use iso_c_binding, only: c_funptr, C_NULL_FUNPTR

    abstract interface
        subroutine func(tag, msg)
            use iso_c_binding, only: c_char
            character(kind=c_char,len=*) :: tag
            character(kind=c_char,len=*) :: msg
        end subroutine func
    end interface

    type, bind(c) :: funcs_t
        type(c_funptr) :: debug = C_NULL_FUNPTR
        type(c_funptr) :: error = C_NULL_FUNPTR
    end type funcs_t

    public :: do_debug, do_error

contains

    subroutine do_debug(conf)
        use iso_c_binding, only: c_f_procpointer
        type(funcs_t), intent(in) :: conf

        procedure(func), pointer :: debug

        call c_f_procpointer(conf%debug, debug)
        call debug("test" // char(0), "hello debug" // char(0))
    end subroutine do_debug


    subroutine do_error(conf)
        use iso_c_binding, only: c_f_procpointer
        type(funcs_t), intent(in) :: conf

        procedure(func), pointer :: error

        call c_f_procpointer(conf%error, error)
        call error("test" // char(0), "hello error" // char(0))
    end subroutine do_error

end module funcpointerinterop
