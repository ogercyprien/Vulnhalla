/**
 * @name Classes
 * @description Maps class definitions for the LLM tool `get_class`
 * @id vulnhalla/python/classes
 */

import python

from Class c
where not c.getLocation().getFile().getAbsolutePath().matches("%site-packages%")
select 
    "Class" as type,
    c.getName() as name,
    c.getLocation().getFile().getAbsolutePath() as file,
    c.getLocation().getStartLine() as start_line,
    c.getLocation().getEndLine() as end_line,
    c.getName() as simple_name
