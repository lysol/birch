#ifndef WORLD_H
#define WORLD_H
#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>

typedef struct {
    PyObject_HEAD
    int chunk_size;
    PyObject *world;
    PyObject *seeded;
    PyObject *batches;
    PyObject *vertex_lists;
    PyObject *bg_batches;
    PyObject *bgs;
} WorldObject;

// module
static PyObject *_module;
static PyObject *graphics;
static PyObject *Batch;
static PyObject *draw;

static PyTypeObject WorldType;
static void World_dealloc(WorldObject *self);
static PyObject *World_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
static int World_init(WorldObject *self, PyObject *args, PyObject *kwds);
static PyMemberDef World_members[];
static PyMethodDef World_methods[];
static PyGetSetDef World_getsets[];
static PyTypeObject WorldType;
#endif
