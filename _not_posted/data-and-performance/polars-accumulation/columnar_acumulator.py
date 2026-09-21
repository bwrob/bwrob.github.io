import polars as pl


class ColumnarMeta(type):
    def __new__(mcs, name, bases, namespace):
        annotations = namespace.get("__annotations__", {})

        if not annotations:
            return super().__new__(mcs, name, bases, namespace)

        fields = list(annotations.keys())
        namespace["__slots__"] = tuple(fields)

        code_lines = []

        code_lines.append("def __init__(self):")
        code_lines.extend(f"    self.{f} = []" for f in fields)
        code_lines.append("")

        args = ", ".join(fields)
        code_lines.append(f"def append(self, *, {args}):")
        code_lines.extend(f"    self.{f}.append({f})" for f in fields)
        code_lines.extend(("", "def to_dict(self):", "    return {"))
        code_lines.extend(f"        '{f}': self.{f}," for f in fields)
        code_lines.append("    }")

        compiled_code = "\n".join(code_lines)

        exec_locals = {}
        exec(compiled_code, {}, exec_locals)

        namespace["__init__"] = exec_locals["__init__"]
        namespace["append"] = exec_locals["append"]
        namespace["to_dict"] = exec_locals["to_dict"]

        return super().__new__(mcs, name, bases, namespace)


class ColumnarModel(metaclass=ColumnarMeta):
    pass


class MagicalUserAccumulator(ColumnarModel):
    id: int
    username: str
    email: str
    age: int
    balance: float
    is_active: bool
    department: str
    role: str


def generate_magical_data():
    data = MagicalUserAccumulator()
    for i in range(10):
        data.append(
            id=i,
            username=f"user_{i}",
            email=f"user_{i}@example.com",
            age=25 + (i % 40),
            balance=i * 2.5,
            is_active=bool(i % 2),
            department="Engineering",
            role="Admin",
        )
    return pl.DataFrame(data.to_dict())


if __name__ == "__main__":
    data = generate_magical_data()
    data.show()
