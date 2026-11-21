(() => {
  const csrfToken = document.querySelector('meta[name="csrf-token"]').content;
  const currency = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
  });
  const deliveryStatuses = [
    "Order Placed",
    "Processing",
    "Shipped",
    "Out for Delivery",
    "Delivered",
  ];

  const checkoutForm = document.querySelector("#checkout-form");
  const paymentForm = document.querySelector("#payment-form");
  const paymentOrder = document.querySelector("#payment-order");
  const paymentAmount = document.querySelector("#payment-amount");
  const ordersList = document.querySelector("#orders-list");
  const deliveryList = document.querySelector("#delivery-list");
  const globalMessage = document.querySelector("#global-message");

  function showMessage(element, message, isError = false) {
    element.textContent = message;
    element.hidden = false;
    element.classList.toggle("is-error", isError);
  }

  function clearMessage(element) {
    element.textContent = "";
    element.hidden = true;
    element.classList.remove("is-error");
  }

  async function sendJson(url, payload) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "The request could not be completed.");
    }
    return result;
  }

  async function getJson(url) {
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    const result = await response.json();
    if (!response.ok) {
      throw new Error(result.error || "The information could not be loaded.");
    }
    return result;
  }

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function updateCheckoutTotals() {
    const price = Number(checkoutForm.elements.price.value) || 0;
    const quantity = Number.parseInt(checkoutForm.elements.quantity.value, 10) || 0;
    const subtotal = price * quantity;
    const delivery = subtotal >= 10000 ? 0 : 499;
    document.querySelector("#subtotal-value").textContent = currency.format(subtotal);
    document.querySelector("#delivery-value").textContent = currency.format(delivery);
    document.querySelector("#total-value").textContent = currency.format(subtotal + delivery);
  }

  function updatePaymentAmount() {
    const selected = paymentOrder.selectedOptions[0];
    paymentAmount.textContent = selected && selected.dataset.total
      ? currency.format(Number(selected.dataset.total))
      : "Select an order";
  }

  checkoutForm.addEventListener("input", updateCheckoutTotals);
  checkoutForm.addEventListener("change", updateCheckoutTotals);
  paymentOrder.addEventListener("change", updatePaymentAmount);

  checkoutForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(document.querySelector("#checkout-message"));
    if (!checkoutForm.reportValidity()) return;

    const fields = new FormData(checkoutForm);
    const payload = {
      name: fields.get("name"),
      email: fields.get("email"),
      phone: fields.get("phone"),
      address: fields.get("address"),
      product_name: fields.get("product_name"),
      price: fields.get("price"),
      quantity: fields.get("quantity"),
    };
    const submitButton = checkoutForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
      const result = await sendJson("/checkout/", payload);
      showMessage(
        document.querySelector("#checkout-message"),
        `${result.message} Order #EM-${String(result.order.id).padStart(5, "0")} · Total ${currency.format(Number(result.order.total_amount))}.`,
      );
      await refreshRecords(result.order.id);
    } catch (error) {
      showMessage(document.querySelector("#checkout-message"), error.message, true);
    } finally {
      submitButton.disabled = false;
    }
  });

  paymentForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearMessage(document.querySelector("#payment-message"));
    if (!paymentForm.reportValidity()) return;

    const submitButton = paymentForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    try {
      const result = await sendJson("/payment/", {
        order_id: paymentOrder.value,
        method: paymentForm.elements.method.value,
      });
      showMessage(document.querySelector("#payment-message"), result.message);
      await refreshRecords(paymentOrder.value);
    } catch (error) {
      showMessage(document.querySelector("#payment-message"), error.message, true);
    } finally {
      submitButton.disabled = false;
    }
  });

  function renderOrders(orders, preferredOrderId) {
    ordersList.replaceChildren();
    document.querySelector("#orders-count").textContent =
      `${orders.length} ${orders.length === 1 ? "order" : "orders"}`;

    const previousSelection = preferredOrderId || paymentOrder.value;
    paymentOrder.replaceChildren(element("option", "", "Select an order"));
    paymentOrder.options[0].value = "";

    orders.forEach((order) => {
      const option = element(
        "option",
        "",
        `#EM-${String(order.id).padStart(5, "0")} · ${order.customer_name}`,
      );
      option.value = order.id;
      option.dataset.total = order.total_amount;
      paymentOrder.append(option);

      const card = element("article", "record-card order-card");
      const main = element("div", "record-main");
      main.append(element("div", "record-icon", "▣"));
      const info = element("div", "record-info");
      const titleRow = element("div", "record-title-row");
      titleRow.append(element("h3", "", order.product_name));
      titleRow.append(element("span", "status-badge", order.order_status));
      info.append(titleRow);
      info.append(element(
        "p",
        "",
        `Order #EM-${String(order.id).padStart(5, "0")} · ${order.customer_name}`,
      ));
      info.append(element("p", "record-date", new Date(order.created_at).toLocaleString()));
      main.append(info);
      card.append(main);

      const side = element("div", "record-side");
      side.append(element("span", "record-total", currency.format(Number(order.total_amount))));
      side.append(element("span", "payment-status", order.payment_status));
      const detailsButton = element("button", "details-button", "View details ⌄");
      detailsButton.type = "button";
      detailsButton.dataset.orderId = order.id;
      const details = element("div", "detail-body");
      details.hidden = true;
      detailsButton.addEventListener("click", async () => {
        if (!details.childElementCount) {
          detailsButton.disabled = true;
          try {
            const result = await getJson(`/orders/${order.id}`);
            const data = result.order;
            [
              ["Email", data.email],
              ["Phone", data.phone],
              ["Address", data.delivery_address],
              ["Payment method", data.payment_method],
            ].forEach(([label, value]) => {
              const row = element("p");
              row.append(element("strong", "", label), document.createTextNode(` ${value}`));
              details.append(row);
            });
            data.items.forEach((item) => {
              const row = element("p");
              row.append(
                element("strong", "", item.product_name),
                document.createTextNode(
                  ` · ${item.quantity} × ${currency.format(Number(item.unit_price))} = ${currency.format(Number(item.line_total))}`,
                ),
              );
              details.append(row);
            });
          } catch (error) {
            details.append(element("p", "is-error", error.message));
          } finally {
            detailsButton.disabled = false;
          }
        }
        details.hidden = !details.hidden;
        detailsButton.textContent = details.hidden ? "View details ⌄" : "Hide details ⌃";
      });
      side.append(detailsButton, details);
      card.append(side);
      ordersList.append(card);
    });

    if (!orders.length) {
      const empty = element("div", "empty-state");
      empty.append(element("span", "empty-icon", "▣"));
      empty.append(element("h3", "", "No orders yet"));
      empty.append(element("p", "", "Your placed orders will appear here."));
      const link = element("a", "", "Start with checkout →");
      link.href = "#checkout";
      empty.append(link);
      ordersList.append(empty);
    }
    if (previousSelection && [...paymentOrder.options].some((option) => option.value === String(previousSelection))) {
      paymentOrder.value = String(previousSelection);
    } else if (orders.length) {
      paymentOrder.value = String(orders[0].id);
    }
    updatePaymentAmount();
  }

  function renderDeliveries(deliveries) {
    deliveryList.replaceChildren();
    deliveries.forEach((delivery) => {
      const card = element("article", "panel delivery-card");
      const top = element("div", "delivery-card-top");
      const heading = element("div");
      const tracking = element("p", "tracking-number");
      tracking.append(document.createTextNode("TRACKING "));
      tracking.append(element("strong", "", delivery.tracking_number));
      heading.append(tracking);
      heading.append(element(
        "h3",
        "",
        `Order #EM-${String(delivery.order_id).padStart(5, "0")} · ${delivery.customer_name}`,
      ));
      top.append(heading, element("span", "status-badge delivery-status-badge", delivery.status));
      card.append(top);

      const facts = element("div", "delivery-facts");
      [
        ["Delivery address", delivery.delivery_address],
        ["Order date", new Date(delivery.order_date).toLocaleDateString()],
        ["Estimated delivery", new Date(`${delivery.estimated_delivery}T00:00:00`).toLocaleDateString()],
      ].forEach(([label, value]) => {
        const fact = element("div");
        fact.append(element("span", "", label), element("strong", "", value));
        facts.append(fact);
      });
      card.append(facts);

      const progress = element("div", "progress-track");
      progress.setAttribute("aria-label", "Delivery progress");
      const completedIndex = deliveryStatuses.indexOf(delivery.status);
      deliveryStatuses.forEach((status, index) => {
        const step = element("div", `progress-step${index <= completedIndex ? " is-complete" : ""}`);
        step.append(element("span", "", String(index + 1)), element("small", "", status));
        progress.append(step);
      });
      card.append(progress);

      const form = element("form", "delivery-update-form");
      const label = element("label", "field");
      label.append(element("span", "", "Update demo tracking status"));
      const select = element("select");
      select.name = "status";
      select.setAttribute("aria-label", "Update delivery status");
      deliveryStatuses.forEach((status) => {
        const option = element("option", "", status);
        option.value = status;
        option.selected = status === delivery.status;
        select.append(option);
      });
      label.append(select);
      const update = element("button", "button button-secondary", "Update status");
      update.type = "submit";
      form.append(label, update);
      card.append(form);
      const message = element("div", "inline-message delivery-message");
      message.setAttribute("role", "status");
      message.setAttribute("aria-live", "polite");
      message.hidden = true;
      card.append(message);
      deliveryList.append(card);
    });

    if (!deliveries.length) {
      const empty = element("div", "empty-state");
      empty.append(element("span", "empty-icon", "⌖"));
      empty.append(element("h3", "", "Nothing on the way yet"));
      empty.append(element("p", "", "Tracking appears as soon as you place an order."));
      const link = element("a", "", "Place an order →");
      link.href = "#checkout";
      empty.append(link);
      deliveryList.append(empty);
    }

    deliveryList.querySelectorAll(".delivery-update-form").forEach((form) => {
      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const card = form.closest(".delivery-card");
        const message = card.querySelector(".delivery-message");
        const button = form.querySelector("button");
        button.disabled = true;
        clearMessage(message);
        try {
          const result = await sendJson(
            `/delivery/${card.dataset.deliveryOrder}`,
            { status: form.elements.status.value },
          );
          showMessage(message, result.message);
          await refreshRecords(paymentOrder.value);
        } catch (error) {
          showMessage(message, error.message, true);
        } finally {
          button.disabled = false;
        }
      });
    });
  }

  async function refreshRecords(preferredOrderId) {
    const [orderData, deliveryData] = await Promise.all([
      getJson("/orders/"),
      getJson("/delivery/"),
    ]);
    renderOrders(orderData.orders, preferredOrderId);
    renderDeliveries(deliveryData.deliveries);
  }

  refreshRecords().catch((error) => showMessage(globalMessage, error.message, true));
})();
