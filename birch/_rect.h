#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>

typedef struct {
    PyObject_HEAD
    int x;
    int y;
    int width;
    int height;
} RectObject;

static PyTypeObject RectType;
static void Rect_dealloc(RectObject *self);
static PyObject *Rect_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int Rect_init(RectObject *self, PyObject *args, PyObject *kwds);
static PyObject *Rect___str__(RectObject *self);
static PyObject *Rect_inflate(RectObject *self, PyObject *args);
static PyObject* Rect_get_right(RectObject* self, void* closure);
static int Rect_set_right(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_bottom(RectObject* self, void* closure);
static int Rect_set_bottom(RectObject* self, PyObject* value, void* closure);
static PyMemberDef Rect_members[];
static PyMethodDef Rect_methods[];
static PyGetSetDef Rect_getsets[];
static PyTypeObject RectType;
static PyModuleDef rect_module;
PyMODINIT_FUNC PyInit__rect(void);
