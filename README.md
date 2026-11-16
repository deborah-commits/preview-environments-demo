# PR preview demo

A small Flask + PostgreSQL task board for a Northflank preview-environments walkthrough.

The app creates its one table and inserts three sample tasks on startup. Existing
tasks and their completion status survive application restarts. Deleted starter
tasks are recreated on a later restart; custom tasks are not recreated.
