#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include "open_simplex.h"

typedef struct {
    PyObject_HEAD
    int seed; /* random seed */
    struct osn_context *ctx;
} OpenSimplexObject;

static void OpenSimplex_dealloc(OpenSimplexObject *self)
{
    Py_XDECREF(self->ctx);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *OpenSimplex_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    OpenSimplexObject *self;
    self = (OpenSimplexObject *) type->tp_alloc(type, 0);
    struct osn_context *ctx;
    if (self != NULL) {
        self->ctx = ctx;
        self->seed = 200; //PyUnicode_FromString("");
    }
    return (PyObject *) self;
}

static int OpenSimplex_init(OpenSimplexObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seed", NULL};
    PyObject *tmp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist,
                                     &self->seed))
        return -1;

    open_simplex_noise(self->seed, &self->ctx);
    Py_INCREF(self->ctx);

    return 0;
}

static PyMemberDef OpenSimplex_members[] = {
    {"seed", T_INT, offsetof(OpenSimplexObject, seed), 0,
     "random seed"},
    {"ctx", T_NONE, offsetof(OpenSimplexObject, ctx), RESTRICTED,
        "opensimplex context"},
    {NULL}  /* Sentinel */
};

static PyObject *OpenSimplex_noise2(OpenSimplexObject *self, PyObject *args) {
    double x;
    double y;
    double res;
    if (!PyArg_ParseTuple(args, "dd", &x, &y))
        return NULL;
    res = open_simplex_noise2(self->ctx, x, y);
    return PyFloat_FromDouble(res);
}

static PyMethodDef OpenSimplex_methods[] = {
    {"noise2", (PyCFunction) OpenSimplex_noise2, METH_VARARGS,
     "OpenSimplex Noise 2D"
    },
    {NULL}  /* Sentinel */
};

static PyTypeObject OpenSimplexType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "open_simplex.OpenSimplex",
    .tp_doc = "A python wrapper for opensimplex c code",
    .tp_basicsize = sizeof(OpenSimplexObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = OpenSimplex_new,
    .tp_init = (initproc) OpenSimplex_init,
    .tp_dealloc = (destructor) OpenSimplex_dealloc,
    .tp_members = OpenSimplex_members,
    .tp_methods = OpenSimplex_methods,
};

static PyModuleDef opensimplex_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "open_simplex",
    .m_doc = "A python wrapper for opensimplex c code.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_open_simplex(void)
{
    PyObject *m;
    if (PyType_Ready(&OpenSimplexType) < 0)
        return NULL;

    m = PyModule_Create(&opensimplex_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&OpenSimplexType);
    PyModule_AddObject(m, "OpenSimplex", (PyObject *) &OpenSimplexType);
    return m;
}

