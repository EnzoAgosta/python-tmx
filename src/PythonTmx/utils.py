from PythonTmx.classes import Bpt, Ept, Inline


def _check_seg(segment: list[Inline | str]) -> None:
  bpt_i = [x.i for x in segment if isinstance(x, Bpt)]
  ept_i = [x.i for x in segment if isinstance(x, Ept)]
  if len(bpt_i) != len(ept_i):
    raise ValueError("Amount of Bpt and Ept elements do not match")
  set_bpt_i = set(bpt_i)
  set_ept_i = set(ept_i)
  if len(set_bpt_i) != len(bpt_i):
    raise ValueError("Duplicate Bpt elements")
  if len(set_ept_i) != len(ept_i):
    raise ValueError("Duplicate Ept elements")
  for bpt, ept in zip(set_bpt_i, set_ept_i):
    if bpt not in set_ept_i:
      raise ValueError(f"Bpt with i={bpt} is missing its corresponding Ept")
    if ept not in set_bpt_i:
      raise ValueError(f"Ept with i={ept} is missing its corresponding Bpt")
