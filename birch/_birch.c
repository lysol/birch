#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>
#include "_birch.h"

static PyModuleDef birch_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_birch",
    .m_doc = "The birch c module",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__birch(void)
{
    _module = PyModule_Create(&birch_module);
    if (_module == NULL)
        return NULL;

    if (PyType_Ready(&PerlinType) < 0)
        return NULL;
    if (PyType_Ready(&RectType) < 0)
        return NULL;
    if (PyType_Ready(&WorldType) < 0)
        return NULL;

    Py_INCREF(&PerlinType);
    PyModule_AddObject(_module, "Perlin", (PyObject *) &PerlinType);
    Py_INCREF(&RectType);
    PyModule_AddObject(_module, "Rect", (PyObject *) &RectType);
    Py_INCREF(&WorldType);
    PyModule_AddObject(_module, "World", (PyObject *) &WorldType);
    graphics = PyImport_ImportModule("pyglet.graphics");
    Batch = PyObject_GetAttrString(graphics, "Batch");
    draw = PyObject_GetAttrString(graphics, "draw");

    return _module;
}

