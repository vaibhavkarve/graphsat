;; All relevant settings for the org → latex → PDF export go here. Reason:
;; local Emacs configurations are not used when running Emacs from the
;; terminal. This file lets us use the same Emacs settings across different
;; machines.


;; The libraries needed for org → latex exporting.
(require 'org)
(require 'ox-latex)


;; We use minted package for formatting of code blocks. (As opposed to
;; lstlistings and verbatim-blocks).
(add-to-list 'org-latex-packages-alist '("" "minted"))
(setq org-latex-listings 'minted)


;; Which languages should be loaded by org-babel?
(org-babel-do-load-languages
 'org-babel-load-languages
 '((R . t)
   (latex . t)
   ;; (python. t)   ;; uncomment to execute python code snippets
   ))

;; Have a frame around the code blocks.
;; This also gives us a place to put code-block labels
(setq org-latex-minted-options
 '(("frame" "lines")))

;; This option is used for adding \ref{}s inside other org blocks and
;; making them work
(setq org-latex-prefer-user-labels t)
