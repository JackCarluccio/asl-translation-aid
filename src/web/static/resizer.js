function resizeSelect(select) {
  const temp = document.createElement("span");
  temp.style.visibility = "hidden";
  temp.style.position = "absolute";
  temp.style.whiteSpace = "nowrap";
  temp.style.font = window.getComputedStyle(select).font;

  temp.textContent = select.options[select.selectedIndex].text;
  document.body.appendChild(temp);

  select.style.width = temp.offsetWidth + 30 + "px"; // +30 for arrow/padding
  document.body.removeChild(temp);
}

document.querySelectorAll("select").forEach(sel => {
  resizeSelect(sel);
  sel.addEventListener("change", () => resizeSelect(sel));
});
