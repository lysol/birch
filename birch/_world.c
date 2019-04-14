#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include <stdio.h>
#include "_world.h"

static void World_dealloc(WorldObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *World_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    WorldObject *self;
    self = (WorldObject *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}

static int World_init(WorldObject *self, PyObject *args, PyObject *kwds)
{
    self->world = PyDict_New();
    self->seeded = PyDict_New();
    self->batches = PyDict_New();
    self->vertex_lists = PyDict_New();
    self->bg_batches = PyDict_New();
    self->bgs = PyDict_New();
    self->chunk_size = 1024;
    return 0;
}

static int *alias(int *ox, int *oy, int chunk_size, int x, int y) {
    *ox = (x - x % chunk_size) / chunk_size;
    *oy = (y - y % chunk_size) / chunk_size;
    return 0;
}

static PyObject *World__alias(WorldObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    return Py_BuildValue("ii",
        ox,
        oy
        );
}

static PyObject *World_unseeded(WorldObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    if (PyDict_Contains(self->seeded, Py_BuildValue("ii", ox, oy))) {
        Py_RETURN_FALSE;
    } else {
        Py_RETURN_TRUE;
    }
}

static PyObject *World__inflate(WorldObject *self, PyObject *args, PyObject *kwargs) {
    int ix, iy, priority = 10;
    static char *keywords[] = {"ix", "iy", "priority", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|i", keywords, &ix, &iy, &priority)) {
        return NULL;
    }
    int changed = 0;
    PyObject *pix = PyLong_FromLong(ix);
    PyObject *piy = PyLong_FromLong(iy);
    PyObject *rdict, *cdict;
    if (!PyDict_Contains(self->world, piy)) {
        rdict = PyDict_New();
        PyDict_SetItem(self->world, piy, rdict);
        changed = 1;
    } else {
        rdict = PyDict_GetItem(self->world, piy);
    }
    if (!PyDict_Contains(rdict, pix)) {
        cdict = PyDict_New();
        PyDict_SetItem(rdict, pix, cdict);
        changed = 1;
    } else {
        cdict = PyDict_GetItem(rdict, pix);
    }
    if (changed) {
        PyObject *batch = PyDict_New();
        PyObject *pgbatch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(self->batches, Py_BuildValue("ii", ix, iy), batch);
        PyDict_SetItem(batch, PyLong_FromLong(priority), pgbatch);
    }
    return Py_None;
}

static PyMemberDef World_members[] = {
    {"chunk_size", T_INT, offsetof(WorldObject, chunk_size), 0,
     "The size of a world chunk"},
    {"world", T_OBJECT_EX, offsetof(WorldObject, world), 0,
     "The actual store of cells."},
    {"seeded", T_OBJECT_EX, offsetof(WorldObject, seeded), 0,
     "Seeded chunks"},
    {"batches", T_OBJECT_EX, offsetof(WorldObject, batches), 0,
     "Chunk batches"},
    {"vertex_lists", T_OBJECT_EX, offsetof(WorldObject, vertex_lists), 0,
     "Chunk vertex_lists"},
    {"bg_batches", T_OBJECT_EX, offsetof(WorldObject, bg_batches), 0,
     "Chunk bg_batches"},
    {"bgs", T_OBJECT_EX, offsetof(WorldObject, bgs), 0,
     "Chunk bgs"},
    {NULL}  /* Sentinel */ };

static PyMethodDef World_methods[] = {
    {"_alias", (PyCFunction) World__alias, METH_VARARGS,
        "Alias a pair of coordinates to a chunk coordinate."},
    {"unseeded", (PyCFunction) World_unseeded, METH_VARARGS,
        "Check if a chunk has been seeded."},
    {"_inflate", (PyCFunction) World__inflate, METH_VARARGS | METH_KEYWORDS,
        "Inflate a chunk before population."},
    {NULL}  /* Sentinel */ };

static PyGetSetDef World_getsets[] = {
    //{"right",  /* name */
    //  (getter) World_get_right,
    //  (setter) World_set_right,
    //  NULL,  /* doc */
    //  NULL /* closure */},
    //{"bottom",  /* name */
    //  (getter) World_get_bottom,
    //  (setter) World_set_bottom,
    //  NULL,  /* doc */
    //  NULL /* closure */},
    {NULL}
};

static PyTypeObject WorldType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "rect.World",
    .tp_doc = "The world storage for birch",
    .tp_basicsize = sizeof(WorldObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = World_new,
    .tp_init = (initproc) World_init,
    .tp_dealloc = (destructor) World_dealloc,
    .tp_members = World_members,
    .tp_methods = World_methods,
    .tp_getset = World_getsets
};

static PyModuleDef world_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "world",
    .m_doc = "The world storage for birch",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__world(void)
{
    if (PyType_Ready(&WorldType) < 0)
        return NULL;

    _module = PyModule_Create(&world_module);
    if (_module == NULL)
        return NULL;

    Py_INCREF(&WorldType);
    PyModule_AddObject(_module, "World", (PyObject *) &WorldType);
    graphics = PyImport_ImportModule("pyglet.graphics");
    Batch = PyObject_GetAttrString(graphics, "Batch");
    draw = PyObject_GetAttrString(graphics, "draw");

    return _module;
}

