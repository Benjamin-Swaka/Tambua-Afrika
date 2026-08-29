/* ============================================================
   CROWDFUNDING JS — Tambua Afrika
   ------------------------------------------------------------
   No external libraries beyond Bootstrap (already loaded on
   the site). Two independent features, each guarded so this
   file can be safely included on any page:

   1. Dynamic add/remove reward rows on the campaign form.
   2. Auto-fill pledge amount when a reward tier is selected.
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {
  initRewardFormset();
  initPledgeRewardSelect();
});

/* ---------- 1. Dynamic reward rows (campaign_form.html) ---------- */

function initRewardFormset() {
  const container = document.getElementById("cf-reward-formset");
  if (!container) return;

  const addBtn = document.getElementById("cf-add-reward-btn");
  const rowsWrapper = container.querySelector(".cf-reward-rows");
  const emptyTemplate = document.getElementById("cf-empty-reward-row");
  const totalFormsInput = container.querySelector(
    'input[name$="-TOTAL_FORMS"]'
  );
  const prefix = container.dataset.prefix;

  // Removing a row: hide it and, if it already exists in the DB,
  // check its DELETE checkbox; if it's a brand-new unsaved row,
  // just remove it from the DOM entirely.
  container.addEventListener("click", function (event) {
    if (!event.target.classList.contains("cf-remove-row-btn")) return;

    const row = event.target.closest(".cf-reward-row");
    const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');

    if (deleteCheckbox) {
      deleteCheckbox.checked = true;
      row.style.display = "none";
    } else {
      row.remove();
      renumberForms();
    }
  });

  if (addBtn && emptyTemplate && totalFormsInput) {
    addBtn.addEventListener("click", function () {
      const formCount = parseInt(totalFormsInput.value, 10);
      const newRowHtml = emptyTemplate.innerHTML.replace(
        /__prefix__/g,
        formCount
      );

      const wrapper = document.createElement("div");
      wrapper.innerHTML = newRowHtml.trim();
      rowsWrapper.appendChild(wrapper.firstElementChild);

      totalFormsInput.value = formCount + 1;
    });
  }

  function renumberForms() {
    // Only relevant when removing brand-new (never-saved) rows,
    // to keep Django's management form TOTAL_FORMS count accurate.
    const remainingRows = rowsWrapper.querySelectorAll(".cf-reward-row");
    if (totalFormsInput) {
      totalFormsInput.value = remainingRows.length;
    }
  }
}

/* ---------- 2. Pledge amount auto-fill (pledge_form.html) ---------- */

function initPledgeRewardSelect() {
  const form = document.getElementById("cf-pledge-form");
  if (!form) return;

  const radios = form.querySelectorAll('input[name="reward_choice"]');
  const hiddenRewardField = document.getElementById("id_reward");
  const amountField = document.getElementById("id_amount");

  if (!radios.length || !amountField) return;

  radios.forEach(function (radio) {
    radio.addEventListener("change", function () {
      if (hiddenRewardField) {
        hiddenRewardField.value = radio.value;
      }

      const amount = radio.dataset.amount;
      if (amount) {
        amountField.value = amount;
        // Amount stays editable — a backer can still increase it
        // above the reward's minimum, but this gives them a sane
        // starting point per the reward tier they picked.
      }
    });
  });
}
