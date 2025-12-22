/**
 * @name Global Variables
 * @description Maps global variable definitions
 * @id vulnhalla/python/global-vars
 */

import python

from AssignStmt a, Name n, Module m
where 
    // The assignment is inside a module (making it global)
    a.getScope() = m
    // The assignment target is a simple Name (e.g., 'x = 1', not 'x.y = 1')
    and a.getATarget() = n
    // Exclude libraries
    and not m.getLocation().getFile().getAbsolutePath().matches("%site-packages%")
select 
    n.getId() as global_var_name,
    m.getLocation().getFile().getAbsolutePath() as file,
    a.getLocation().getStartLine() as start_line,
    a.getLocation().getEndLine() as end_line
