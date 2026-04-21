"""Demo of the timeseriesanalysis Python package. See README.md for setup."""

from timeseriesanalysis import Vec


def main() -> None:
    vec = Vec()

    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]

    add_result = list(vec.Add(a, b))
    add_scalar_result = list(vec.Add(a, 10.0))
    subtract_result = list(vec.Subtract(b, a))
    multiply_result = list(vec.Multiply(a, b))
    multiply_scalar_result = list(vec.Multiply(a, 2.0))

    print(f"Add:             {a} + {b} = {add_result}")
    print(f"Add scalar:      {a} + 10  = {add_scalar_result}")
    print(f"Subtract:        {b} - {a} = {subtract_result}")
    print(f"Multiply:        {a} * {b} = {multiply_result}")
    print(f"Multiply scalar: {a} * 2   = {multiply_scalar_result}")

    data = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0]
    mean = vec.Mean(data)
    total = vec.Sum(data)
    minimum = vec.Min(data)
    maximum = vec.Max(data)

    print()
    print(f"Stats for {data}:")
    print(f"  Mean: {mean}")
    print(f"  Sum:  {total}")
    print(f"  Min:  {minimum}")
    print(f"  Max:  {maximum}")


if __name__ == "__main__":
    main()
