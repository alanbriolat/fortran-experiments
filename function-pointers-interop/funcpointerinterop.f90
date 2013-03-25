module funcpointerinterop

    use iso_c_binding, only: c_funptr

    abstract interface
        subroutine func(data)
            use iso_c_binding, only: c_int
            integer(c_int), value :: data
        end subroutine func
    end interface

    type, bind(c) :: funcs_t
        type(c_funptr) :: debug = 0
        type(c_funptr) :: error = 0
    end type funcs_t

    public :: do_debug, do_error

contains

    subroutine do_debug(conf)
        use iso_c_binding, only: c_f_procpointer
        type(funcs_t), intent(in) :: conf

        procedure(func), pointer :: debug

        call c_f_procpointer(conf%debug, debug)
        call debug(22)
    end subroutine do_debug


    subroutine do_error(conf)
        use iso_c_binding, only: c_f_procpointer
        type(funcs_t), intent(in) :: conf

        procedure(func), pointer :: error

        call c_f_procpointer(conf%error, error)
        call error(33)
    end subroutine do_error

end module funcpointerinterop
