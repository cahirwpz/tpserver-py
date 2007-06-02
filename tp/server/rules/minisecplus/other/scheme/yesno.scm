(lambda (design bits) 
	(let ((n (apply + bits))) 
		(cons n 
			(if (> n 1) "Yes" "No"))))
