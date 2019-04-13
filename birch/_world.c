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

static PyObject *World__alias(WorldObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    return Py_BuildValue("ii",
        (x - x % self->chunk_size) / self->chunk_size,
        (y - y % self->chunk_size) / self->chunk_size
        );
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
    PyObject *m;
    if (PyType_Ready(&WorldType) < 0)
        return NULL;

    m = PyModule_Create(&world_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&WorldType);
    PyModule_AddObject(m, "World", (PyObject *) &WorldType);
    return m;
}

