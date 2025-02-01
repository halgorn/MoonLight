
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftPLUSMINUSleftMULTIPLYDIVIDEASSIGN DIVIDE IDENTIFIER LPAREN MINUS MULTIPLY NUMBER PLUS RPARENprogram : program statementprogram : statementstatement : IDENTIFIER ASSIGN expressionexpression : expression PLUS expression\n                  | expression MINUS expression\n                  | expression MULTIPLY expression\n                  | expression DIVIDE expressionexpression : LPAREN expression RPARENexpression : NUMBERexpression : IDENTIFIER'
    
_lr_action_items = {'IDENTIFIER':([0,1,2,4,5,6,7,8,9,10,11,12,13,15,16,17,18,19,],[3,3,-2,-1,6,-10,-3,6,-9,6,6,6,6,-4,-5,-6,-7,-8,]),'$end':([1,2,4,6,7,9,15,16,17,18,19,],[0,-2,-1,-10,-3,-9,-4,-5,-6,-7,-8,]),'ASSIGN':([3,],[5,]),'LPAREN':([5,8,10,11,12,13,],[8,8,8,8,8,8,]),'NUMBER':([5,8,10,11,12,13,],[9,9,9,9,9,9,]),'PLUS':([6,7,9,14,15,16,17,18,19,],[-10,10,-9,10,-4,-5,-6,-7,-8,]),'MINUS':([6,7,9,14,15,16,17,18,19,],[-10,11,-9,11,-4,-5,-6,-7,-8,]),'MULTIPLY':([6,7,9,14,15,16,17,18,19,],[-10,12,-9,12,12,12,-6,-7,-8,]),'DIVIDE':([6,7,9,14,15,16,17,18,19,],[-10,13,-9,13,13,13,-6,-7,-8,]),'RPAREN':([6,9,14,15,16,17,18,19,],[-10,-9,19,-4,-5,-6,-7,-8,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'program':([0,],[1,]),'statement':([0,1,],[2,4,]),'expression':([5,8,10,11,12,13,],[7,14,15,16,17,18,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> program","S'",1,None,None,None),
  ('program -> program statement','program',2,'p_program_multiple','parser.py',14),
  ('program -> statement','program',1,'p_program_single','parser.py',18),
  ('statement -> IDENTIFIER ASSIGN expression','statement',3,'p_statement_assign','parser.py',25),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','parser.py',32),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','parser.py',33),
  ('expression -> expression MULTIPLY expression','expression',3,'p_expression_binop','parser.py',34),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','parser.py',35),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','parser.py',39),
  ('expression -> NUMBER','expression',1,'p_expression_number','parser.py',43),
  ('expression -> IDENTIFIER','expression',1,'p_expression_identifier','parser.py',47),
]
