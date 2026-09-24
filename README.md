### Aberdeen: Lisp-like language with a website and a visual interpreter.
Syntax examples:
  `# Hello world program`
  (print "hello, world!");

  `# Factorial program`
  (set "x" 10);
  (set "t" 1);
  (set "i" 1);
  (while (! (= $i (+ $x 1)))
      (set "t" (* $t $i))
      (set "i" (+ $i 1)));
  (print "factorial of " $x " is " $t);
  
