This didactic narrative follows a developer probing the runtime with five sequential
experiments. Each experiment challenges an intuitive assumption about memory,\
revealing how virtual machines manage lifecycles, execution stacks, and object\
ownership.\
──────

### Act I: The Illusion of Dynamic Lifecycles

#### Question: "How many references exist for a fundamental constant?"

• Intuition: An integer like 1 is just a basic value. If passed into an inspection\
function, it should have a reference count of 1 or 2.\
• The Probe:\
\>>> import sys\
\>>> sys.getrefcount(1)\
4294967295

• The Revelation (PEP 683 — Immortality):\
4294967295 is 2³² - 1 (UINT32_MAX). The runtime did not calculate references; it\
returned a sentinel refcount.\
• Systems Lesson:\
In a high-throughput runtime, tracking every increment and decrement of ubiquitous\
singletons (None, True, (), small ints [-5, 256]) causes extreme cache contention and
CPU churn. Under PEP 683, CPython marks these objects as immortal.\
• Py_INCREF and Py_DECREF treat the sentinel as a no-op.\
• The Garbage Collector ignores them during cycle detection.\
• Their lifecycle spans the entire life of the runtime process.

──────

### Act II: The Invisible Hand of the Compiler

#### Question: "What holds references to a standard variable?"

• Intuition: Let's pick a number outside the immortal pool (1111) and bind it to a\
single variable v. We expect exactly 2 references: one from variable v, and one\
temporary reference created by passing it to sys.getrefcount().\
• The Probe:\
\>>> v = 1111\
\>>> sys.getrefcount(v)\
4

• The Revelation (Compile-Time Materialization):\
The count is 4, not 2. Who else is holding 1111?\
1\. globals()['v'] (the variable name in the module dictionary).\
2\. The evaluation stack (loading v for the function call).\
3\. code.co_consts: Because 1111 was a literal in source code, Python's compiler\
instantiated the integer object at compile time and stored it inside the code\
object's constant tuple.\
4\. The Parser Token Cache: The interactive CLI / compiler pipeline keeps an AST\
token sequence referencing parsed tokens.\
• Systems Lesson:\
Code is not just instructions; it is an object graph. Literals written in source code
exist in memory before execution even begins, rooted inside code objects and metadata
structures.\
──────

### Act III: Isolating Pure Runtime Allocation

#### Question: "Can we decouple an object from the compiler's constant table?"

• Intuition: If we prevent the compiler from seeing the literal 1111 during\
compilation, the extra constant references should disappear.\
• The Probe:\
\>>> v = int("1111")\
\>>> sys.getrefcount(v)\
2

• The Revelation (Mortal Heap Lifecycle):\
By hiding the number behind a runtime string parsing function, the compiler cannot\
pre-allocate 1111 into co_consts.\
• Systems Lesson:\
Now the integer is genuinely allocated on the heap at runtime. The reference\
accounting is completely transparent and matches our original hypothesis:\
$$\text{Refcount} = \underbrace{1}{\text{Namespace Dict } (v)} +
\underbrace{1}{\text{VM Evaluation Stack}} = 2$$\
──────

### Act IV: The Cost of Crossing Function Boundaries

#### Question: "What happens when an anonymous object enters a function?"

• Intuition: If an object has no variable name (object()), it should have 0 permanent
references. Passing it into a user function should give it a temporary refcount.\
• The Probe:\
\>>> def inspect(x):\
... return sys.getrefcount(x)\
...\
\>>> inspect(object())\
2

• The Revelation (Python Stack Frame Overhead):\
Where do the 2 references come from?
1\. Caller's Frame: The caller's operand evaluation stack holds the return value\
of object().
2\. Callee's Frame: Calling a Python function instantiates a new PyFrameObject.\
The argument is bound into the function's local variable slot array
(fastlocals[0] = x), creating an explicit reference.
• Systems Lesson:
In a managed language, calling a user function is not a simple jump; it allocates a\
frame activation record that roots and retains all arguments for the duration of the
function's scope.
──────

### Act V: The Zero-Cost Abstraction of Borrowed Pointers

#### Question: "Can an object ever be observed alive with a refcount of 1?"

• Intuition: If passing an argument to any function requires a reference, it seems\
mathematically impossible for sys.getrefcount to ever report 1.
• The Probe:
\>>> sys.getrefcount(object())
1

• The Revelation (PEP 590 — Vectorcall & Borrowed References):
sys.getrefcount is a built-in C function. Unlike Python functions:
1\. It does not allocate a PyFrameObject.
2\. Modern CPython uses the Vectorcall protocol, which passes arguments as a raw C
pointer array (PyObject \*const \*args) pointing directly into the caller's\
evaluation stack.
3\. C functions can inspect objects via borrowed references without issuing\
Py_INCREF.
• Systems Lesson:
object() is born on the evaluation stack with an initial refcount of 1. The C\
function peeks at obj->ob_refcnt via a borrowed pointer, reading 1.
The moment the statement finishes, the evaluation stack pops the temporary object,\
the refcount drops from 1 → 0, and the memory is reclaimed immediately without ever\
surviving past that single bytecode evaluation.
──────

### 🗺️ Conceptual Summary Matrix

Experiment │ Code │ Result │ Mechanism Revealed
────────────────────────┼────────────────────────┼─────────┼─────────────────────────
I. Immortality │ sys.getrefcount(1) │ 4294967 │ PEP 683 saturated
│ │ 295 │ sentinel refcount; GC-
│ │ │ exempt singletons.
II. Static Constants │ v = 1111; │ 4 │ co_consts tuple + AST
│ sys.getrefcount(v) │ │ parser token caches
│ │ │ holding literals.
III. Pure Runtime │ v = int('1111'); │ 2 │ Mortal heap allocation:
│ sys.getrefcount(v) │ │ namespace dictionary +
│ │ │ evaluation stack.
IV. Call Frames │ def f(x): │ 2 │ Python frame
│ sys.getrefcount(x) │ │ allocation; argument
│ │ │ binding into
│ │ │ fastlocals.
V. Ephemeral │ sys.getrefcount(object │ 1 │ Evaluation stack
Lifecycles │ ()) │ │ ownership + C
│ │ │ Vectorcall borrowed
│ │ │ references.
