#ifndef RECT_H
#define RECT_H
#include <Python.h>
#include <structmember.h>

#define collidepoint(rect, x, y) (x >= rect->x && x < rect->x + rect->width && \
        y >= rect->y && y < rect->y + rect->height)

#define colliderect(first, second) ( \
        !((second->x + second->width - 1) < first->x || second->x > (first->x + first->width - 1) || \
        (second->y + second->height - 1) < first->y || second->y > (first->y + first->height - 1)) \
        )

typedef struct {
    PyObject_HEAD
    int x;
    int y;
    int width;
    int height;
} RectObject;

typedef struct {
    int x;
    int y;
    int width;
    int height;
} RectShallow;

static PyTypeObject RectType;
static void Rect_dealloc(RectObject *self);
static PyObject *Rect_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int Rect_init(RectObject *self, PyObject *args, PyObject *kwds);
static PyObject *Rect___str__(RectObject *self);
static PyObject *Rect_inflate(RectObject *self, PyObject *args);
static PyObject *Rect_collidepoint(RectObject *self, PyObject *args);
static PyObject *Rect_colliderect(RectObject *self, PyObject *args);
static PyObject* Rect_get_right(RectObject* self, void* closure);
static int Rect_set_right(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_bottom(RectObject* self, void* closure);
static int Rect_set_bottom(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_center(RectObject* self, void* closure);
static int Rect_set_center(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_position(RectObject* self, void* closure);
static int Rect_set_position(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_topright(RectObject* self, void* closure);
static int Rect_set_topright(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_bottomleft(RectObject* self, void* closure);
static int Rect_set_bottomleft(RectObject* self, PyObject* value, void* closure);
static PyObject* Rect_get_bottomright(RectObject* self, void* closure);
static int Rect_set_bottomright(RectObject* self, PyObject* value, void* closure);
static PyMemberDef Rect_members[];
static PyMethodDef Rect_methods[];
static PyGetSetDef Rect_getsets[];
static PyTypeObject RectType;
#endif
