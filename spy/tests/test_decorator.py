from spy.decorator import f64, i32, spy


class TestSpyDecorator:
    def test_add_i32(self):
        @spy
        def add(x: i32, y: i32) -> i32:
            return x + y

        assert add(3, 4) == 7
        assert add(-1, 1) == 0

    def test_mul_f64(self):
        @spy
        def mul(x: f64, y: f64) -> f64:
            return x * y

        assert abs(mul(1.5, 2.0) - 3.0) < 1e-9

    def test_identity_i32(self):
        @spy
        def identity(x: i32) -> i32:
            return x

        assert identity(42) == 42
        assert identity(-100) == -100

    def test_conditional(self):
        @spy
        def abs_val(x: i32) -> i32:
            if x < 0:
                return -x
            return x

        assert abs_val(5) == 5
        assert abs_val(-5) == 5
