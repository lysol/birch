#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include <stdio.h>
#include "_rect.h"

static void Rect_dealloc(RectObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *Rect_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    RectObject *self;
    self = (RectObject *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}

static int Rect_init(RectObject *self, PyObject *args, PyObject *kwds)
{
    if (!PyArg_ParseTuple(args, "iiii", &self->x, &self->y, &self->width, &self->height))
        return -1;
    return 0;
}

static PyObject *Rect___str__(RectObject *self) {
    char buffer[100];
    sprintf(buffer, "<Rect %d,%d %dx%d>", self->x, self->y,
                self->width, self->height);
    return PyUnicode_FromString(buffer);
}

static PyObject *Rect_inflate(RectObject *self, PyObject *args) {
    int w, h;
    if (!PyArg_ParseTuple(args, "ii", &w, &h)) {
        return NULL;
    }
    int whalf = w / 2;
    int hhalf = h / 2;
    int newx = self->x - whalf;
    int newy = self->y - hhalf;
    int newwidth = self->width + whalf;
    int newheight = self->height + hhalf;
    PyObject *nargs = Py_BuildValue("iiii", newx, newy, newwidth, newheight);
    RectObject *newrect;
    newrect = (RectObject *) RectType.tp_alloc(&RectType, 0);
    Rect_init(newrect, nargs, NULL);
    Py_DECREF(nargs);
    return (PyObject *)newrect;
}


static PyObject* Rect_get_right(RectObject* self, void* closure) {
    return PyLong_FromLong(self->x + self->width);
}

static int Rect_set_right(RectObject* self, PyObject* value, void* closure) {
    int i = (int)PyLong_AsLong(value);
    if (i < self->x) {
        PyErr_SetString(PyExc_RuntimeError, "Right coordinate can not be smaller than top.");
    }
    if (PyErr_Occurred()) {
        return -1;
    }
    self->width = i - self->x;
    return 0;
}

static PyObject* Rect_get_bottom(RectObject* self, void* closure) {
    return PyLong_FromLong(self->y + self->height);
}

static int Rect_set_bottom(RectObject* self, PyObject* value, void* closure) {
    int i = (int)PyLong_AsLong(value);
    if (i < self->y) {
        PyErr_SetString(PyExc_RuntimeError, "Bottom coordinate can not be smaller than top.");
    }
    if (PyErr_Occurred()) {
        return -1;
    }
    self->height = i - self->y;
    return 0;
}

static PyObject* Rect_get_center(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("ii",
            self->x + self->width / 2,
            self->y + self->height / 2);
    return point;
}

static int Rect_set_center(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a two value (x,y) sequence.");
        return -1;
    }
    PyObject *newcx = PySequence_GetItem(value, 0);
    PyObject *newcy = PySequence_GetItem(value, 1);
    int ncx = (int)PyLong_AsLong(newcx);
    int ncy = (int)PyLong_AsLong(newcy);
    self->x = ncx - self->width / 2;
    self->y = ncy - self->height / 2;
    return 0;
}

static PyMemberDef Rect_members[] = {
    {"x", T_INT, offsetof(RectObject, x), 0,
     "The horizontal coordinate of the top left origin point."},
    {"y", T_INT, offsetof(RectObject, y), 0,
     "The vertical coordinate of the top left origin point."},
    {"top", T_INT, offsetof(RectObject, y), 0,
     "The vertical coordinate of the top left origin point."},
    {"left", T_INT, offsetof(RectObject, x), 0,
     "The vertical coordinate of the top left origin point."},
    {"width", T_INT, offsetof(RectObject, width), 0,
     "The width of the rectangle."},
    {"height", T_INT, offsetof(RectObject, height), 0,
     "The height of the rectangle."},
    {NULL}  /* Sentinel */ };

static PyMethodDef Rect_methods[] = {
    {"__str__", (PyCFunction) Rect___str__, METH_NOARGS,
        "String representation of a Rect."},
    {"inflate", (PyCFunction) Rect_inflate, METH_VARARGS,
        "Inflate a rectangle and return a new instance."},
    {NULL}  /* Sentinel */ };

static PyGetSetDef Rect_getsets[] = {
    {"right",  /* name */
        (getter) Rect_get_right,
        (setter) Rect_set_right,
        NULL,  /* doc */
        NULL /* closure */},
    {"bottom",  /* name */
        (getter) Rect_get_bottom,
        (setter) Rect_set_bottom,
        NULL,  /* doc */
        NULL /* closure */},
    {"center",  /* name */
        (getter) Rect_get_center,
        (setter) Rect_set_center,
        NULL,  /* doc */
        NULL /* closure */},
    {NULL}
};

/*
static PyObject *Perlin_noise2_bytes(PerlinObject *self, PyObject *args) {
    int x;
    int y;
    double freq;
    int size;
    int octaves;
    int pixvalue;
    if (!PyArg_ParseTuple(args, "iidiii", &x, &y, &freq, &octaves, &size, &pixvalue))
        return NULL;
*/

static PyTypeObject RectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "rect.Rect",
    .tp_doc = "A fast rectangle helper object",
    .tp_basicsize = sizeof(RectObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Rect_new,
    .tp_init = (initproc) Rect_init,
    .tp_dealloc = (destructor) Rect_dealloc,
    .tp_members = Rect_members,
    .tp_methods = Rect_methods,
    .tp_getset = Rect_getsets
};

static PyModuleDef rect_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "rect",
    .m_doc = "A fast rectangle helper object.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__rect(void)
{
    PyObject *m;
    if (PyType_Ready(&RectType) < 0)
        return NULL;

    m = PyModule_Create(&rect_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&RectType);
    PyModule_AddObject(m, "Rect", (PyObject *) &RectType);
    return m;
}

