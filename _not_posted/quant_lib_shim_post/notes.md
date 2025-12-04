## How to Add Type Annotations to Unannotated Python Code

### 1. Adding Types with Stub Files (`.pyi`)

Stub files allow you to add type annotations to a Python module without modifying its source code (`.py` file).

* **Location:** The `.pyi` stub file must have the **exact same name** as the Python module it annotates and be placed in the same directory.
* **Syntax:**
    * You only define function/method signatures (with types) and class/module-level attributes.
    * All implementation logic (function bodies, class bodies) is replaced with an ellipsis (`...`).
* **Generation:**
    * **Manual:** You can write the `.pyi` file by hand.
    * **Automated (Static):** You can use `stubgen` (a tool included with `mypy`) to generate a draft stub file. This file will be filled with `Any` types, which you must then manually refine.

---

### 2. The "Typed Shim" Pattern for Third-Party Libraries

This pattern is used to create a typed wrapper around an unannotated third-party library. It involves two files in your wrapper package (e.g., `my_wrapper/`):

1.  **`__init__.py` (For Python at Runtime)**
    * This file imports the *actual, functional objects* from the unannotated third-party library.
    * It exposes them as the public API of your wrapper.
    * Python executes this file when your code runs.

2.  **`__init__.pyi` (For Type Checkers)**
    * This file **re-declares** the signatures of the objects you imported in `__init__.py`.
    * You **must not** import the objects from the third-party library here; instead, you write their typed signatures from scratch.
    * Type checkers like **Pyright** and **Mypy** will *always* read this `.pyi` file for type information and **completely ignore** the `__init__.py` file.

---

### 3. Automatic Type Inference

Instead of writing stubs by hand, you can use tools to infer types by observing your code.

* **MonkeyType (Runtime Inference):**
    * **How it works:** It "watches" your code (e.g., your test suite) as it runs and records the actual types of arguments and return values.
    * **Usage:**
        1.  Run your code: `monkeytype run -m pytest`
        2.  Generate stubs: `monkeytype stub my_module`
    * This produces a high-quality draft `.pyi` file based on real-world usage.

* **pytype (Static Inference):**
    * **How it works:** It analyzes your code's bytecode without running it to infer types.
    * **Usage:** `pytype my_module.py` (generates a stub in `.pytype/pyi/`).
