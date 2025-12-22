/**
 * @name Function Tree
 * @description Generates a call graph and scope map (Function/Class/Module) for Vulnhalla.
 * @id vulnhalla/python/function-tree
 */

import python

/**
 * Generates the unique ID used by Vulnhalla.
 */
string get_scope_id(Scope s) {
    result = s.getLocation().getFile().getAbsolutePath() + ":" + s.getLocation().getStartLine()
}

/**
 * Get the end line.
 * We calculate the max of the scope's reported end line AND the end line of any statement within it.
 * This ensures that Class/Function scopes include their bodies, and Modules include all content.
 */
int get_end_line(Scope s) {
    result = max(int l |
        l = s.getLocation().getEndLine() or
        exists(Stmt st | st.getScope() = s | l = st.getLocation().getEndLine())
    | l)
}

/**
 * Predicate to find callers. 
 */
string get_caller(Scope s) {
    if s instanceof Function then
        exists(Function f | f = s |
            if exists(Function caller, Call c, FunctionObject obj |
                c.getScope() = caller and
                obj.getFunction() = f and
                obj.getACall().getNode() = c
            )
            then exists(Function caller, Call c, FunctionObject obj |
                c.getScope() = caller and
                obj.getFunction() = f and
                obj.getACall().getNode() = c
                | result = get_scope_id(caller)
            )
            else result = ""
        )
    else
        result = ""
}

from Scope s
where 
    // Exclude libraries
    not s.getLocation().getFile().getAbsolutePath().matches("%site-packages%")
    // Exclude tests
    and not s.getLocation().getFile().getAbsolutePath().matches("%/test/%")
    // Filter out built-in functions (they have no location)
    and exists(s.getLocation())
select 
    s.getName() as function_name,
    s.getLocation().getFile().getAbsolutePath() as file,
    s.getLocation().getStartLine() as start_line,
    get_scope_id(s) as function_id,
    get_end_line(s) as end_line,
    get_caller(s) as caller_id
