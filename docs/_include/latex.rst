.. role:: cite
.. role:: bibstyle
.. role:: bib

.. role:: endpoint
.. role:: http
.. role:: method
.. role:: kw
.. role:: model
.. role:: topic

.. section-numbering::
    :depth: 1
    :suffix: .

.. raw:: latex

  \reversemarginpar
  \def\marginparwidth{1in}

  \newcommand{\DUrolehttp}[1]{{\ttfamily#1}}
  \newcommand{\DUrolemodel}[1]{{\itshape#1}}
  \ifx\lstset\undefined\else\lstset{basicstyle=\scriptsize\ttfamily, frame=single}\fi
  \newcommand{\DUroleendpoint}[1]{{\ttfamily#1}}
  \newcommand{\DUrolekw}[1]{{\bfseries\ttfamily#1}}
  \newcommand{\DUrolemethod}[1]{{\bfseries\ttfamily#1}}
  \newcommand{\DUroletopic}[1]{\marginpar{\scriptsize\itshape\vspace{0.5\baselineskip}#1}}

  \providecommand*\DUrolecite[1]{\cite{#1}}
  \providecommand*\DUrolebibstyle[1]{\bibliographystyle{#1}}
  \providecommand*\DUrolebib[1]{\bibliography{#1}}

  \hypersetup%
  {%
    bookmarksnumbered=true,
    bookmarksopen=true,
    bookmarksopenlevel=1,
    colorlinks=true,
    breaklinks=true,
    pdfborder={0 0 1},
    citecolor=blue,
    linkcolor=blue,
    anchorcolor=black,
    urlcolor=blue%
  }
