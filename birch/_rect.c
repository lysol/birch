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

static PyObject *Rect_collidepoint(RectObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    if (x >= self->x && x < self->x + self->width &&
            y >= self->y && y < self->y + self->height) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}

static PyObject *Rect_colliderect(RectObject *self, PyObject *args) {
    RectObject *other;
    if (!PyArg_ParseTuple(args, "O", &other)) {
        return NULL;
    }
    if (other->x + other->width - 1 < self->x ||
        other->x > self->x + self->width - 1 ||
        other->y + other->height - 1 < self->y ||
        other->y > self->y + self->height - 1) {
        Py_RETURN_FALSE;
    } else {
        Py_RETURN_TRUE;
    }
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

static PyObject* Rect_get_position(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("ii",
            self->x,
            self->y);
    return point;
}

static int Rect_set_position(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a two value (x,y) sequence.");
        return -1;
    }
    PyObject *newx = PySequence_GetItem(value, 0);
    PyObject *newy = PySequence_GetItem(value, 1);
    int nx = (int)PyLong_AsLong(newx);
    int ny = (int)PyLong_AsLong(newy);
    self->x = nx;
    self->y = ny;
    return 0;
}

static PyObject* Rect_get_bounds(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("iiii",
            self->x,
            self->y,
            self->width,
            self->height);
    return point;
}

static int Rect_set_bounds(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a four value (x,y,w,h) sequence.");
        return -1;
    }
    PyObject *newx = PySequence_GetItem(value, 0);
    PyObject *newy = PySequence_GetItem(value, 1);
    PyObject *neww = PySequence_GetItem(value, 2);
    PyObject *newh = PySequence_GetItem(value, 3);
    int nx = (int)PyLong_AsLong(newx);
    int ny = (int)PyLong_AsLong(newy);
    int nw = (int)PyLong_AsLong(neww);
    int nh = (int)PyLong_AsLong(newh);
    self->x = nx;
    self->y = ny;
    self->width = nw;
    self->height = nh;
    return 0;
}

static PyObject* Rect_get_topright(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("ii",
            self->x + self->width,
            self->y);
    return point;
}

static int Rect_set_topright(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a two value (x,y) sequence.");
        return -1;
    }
    PyObject *newr = PySequence_GetItem(value, 0);
    PyObject *newy = PySequence_GetItem(value, 1);
    int nr = (int)PyLong_AsLong(newr);
    int ny = (int)PyLong_AsLong(newy);
    self->x = nr - self->width;
    self->y = ny;
    return 0;
}

static PyObject* Rect_get_bottomleft(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("ii",
            self->x,
            self->y + self->height);
    return point;
}

static int Rect_set_bottomleft(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a two value (x,y) sequence.");
        return -1;
    }
    PyObject *newx = PySequence_GetItem(value, 0);
    PyObject *newb = PySequence_GetItem(value, 1);
    int nx = (int)PyLong_AsLong(newx);
    int nb = (int)PyLong_AsLong(newb);
    self->x = nx;
    self->y = nb - self->height;
    return 0;
}

static PyObject* Rect_get_bottomright(RectObject* self, void* closure) {
    PyObject *point = Py_BuildValue("ii",
            self->x + self->width,
            self->y + self->height);
    return point;
}

static int Rect_set_bottomright(RectObject* self, PyObject* value, void* closure) {
    if (PySequence_Length(value) != 2) {
        PyErr_SetString(PyExc_RuntimeError, "Coordinates must be a two value (x,y) sequence.");
        return -1;
    }
    PyObject *newr = PySequence_GetItem(value, 0);
    PyObject *newb = PySequence_GetItem(value, 1);
    int nr = (int)PyLong_AsLong(newr);
    int nb = (int)PyLong_AsLong(newb);
    self->x = nr - self->width;
    self->y = nb - self->height;
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
    {"w", T_INT, offsetof(RectObject, width), 0,
     "The width of the rectangle."},
    {"h", T_INT, offsetof(RectObject, height), 0,
     "The height of the rectangle."},
    {NULL}  /* Sentinel */ };

static PyMethodDef Rect_methods[] = {
    {"__str__", (PyCFunction) Rect___str__, METH_NOARGS,
        "String representation of a Rect."},
    {"inflate", (PyCFunction) Rect_inflate, METH_VARARGS,
        "Inflate a rectangle and return a new instance."},
    {"collidepoint", (PyCFunction) Rect_collidepoint, METH_VARARGS,
        "Check if another point collides with this one"},
    {"colliderect", (PyCFunction) Rect_colliderect, METH_VARARGS,
        "Check if another rect collides with this one"},
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
    {"position",  /* name */
        (getter) Rect_get_position,
        (setter) Rect_set_position,
        NULL,  /* doc */
        NULL /* closure */},
    {"bounds",  /* name */
        (getter) Rect_get_bounds,
        (setter) Rect_set_bounds,
        NULL,  /* doc */
        NULL /* closure */},
    {"topleft",  /* name */
        (getter) Rect_get_position,
        (setter) Rect_set_position,
        NULL,  /* doc */
        NULL /* closure */},
    {"topright",  /* name */
        (getter) Rect_get_topright,
        (setter) Rect_set_topright,
        NULL,  /* doc */
        NULL /* closure */},
    {"bottomleft",  /* name */
        (getter) Rect_get_bottomleft,
        (setter) Rect_set_bottomleft,
        NULL,  /* doc */
        NULL /* closure */},
    {"bottomright",  /* name */
        (getter) Rect_get_bottomright,
        (setter) Rect_set_bottomright,
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

