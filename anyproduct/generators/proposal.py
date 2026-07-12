"""Lawn care proposal generator."""
from __future__ import annotations

from datetime import datetime
from typing import Mapping

from .base import Generator, GeneratorResult


class LawnProposalGenerator(Generator):
    slug = "proposal"
    name = "Lawn Care Proposal"
    description = "Create a professional lawn maintenance proposal from JSON data."

    @classmethod
    def example_input(cls) -> Mapping[str, object]:
        return {
            "client": {
                "name": "Alex Rivera",
                "address": "123 Meadow Lane",
                "email": "alex@example.com",
                "phone": "555-0123",
            },
            "property": {
                "size_sq_ft": 4800,
                "description": "Front and back yard with perennial beds and mature trees.",
            },
            "services": [
                {
                    "name": "Mowing & Edging",
                    "description": "Weekly mowing during the growing season with clean edging.",
                    "frequency": "Weekly",
                    "price": 55.0,
                },
                {
                    "name": "Seasonal Fertilization",
                    "description": "Four-application program with soil-friendly fertilizers.",
                    "frequency": "Quarterly",
                    "price": 95.0,
                },
            ],
            "schedule": {
                "start_date": "2024-04-01",
                "end_date": "2024-11-15",
                "notes": "Service windows can be adjusted based on weather patterns.",
            },
            "pricing": {
                "currency": "USD",
                "discount": 0.05,
                "additional_notes": "Loyalty discount applied when committing to a full season.",
            },
            "company": {
                "name": "Green Horizons Landscaping",
                "representative": "Jamie Patel",
                "email": "hello@greenhorizons.test",
            },
        }

    def generate(self, payload: Mapping[str, object]) -> GeneratorResult:
        data = dict(payload)
        client = data.get("client", {})
        property_details = data.get("property", {})
        services = list(data.get("services", []))
        schedule = data.get("schedule", {})
        pricing = data.get("pricing", {})
        company = data.get("company", {})

        client_name = client.get("name", "Valued Client")
        company_name = company.get("name", "Your Company")
        title = f"{company_name} Lawn Care Proposal for {client_name}"

        result = GeneratorResult(title=title)

        intro_lines = [
            f"Thank you {client_name} for considering {company_name} for your lawn care needs.",
        ]
        if property_details.get("description"):
            intro_lines.append(f"Property overview: {property_details['description']}")
        if property_details.get("size_sq_ft"):
            intro_lines.append(
                f"Estimated property size: {property_details['size_sq_ft']:,} square feet."
            )
        result.summary = " ".join(intro_lines)

        if services:
            service_paragraphs = []
            currency = pricing.get("currency", "USD")
            for service in services:
                line = (
                    f"{service.get('name', 'Service')}: {service.get('description', '').strip()}"
                )
                if service.get("frequency"):
                    line += f" (Frequency: {service['frequency']})"
                if service.get("price") is not None:
                    line += f" — {currency} {service['price']:.2f}"
                service_paragraphs.append(line)
            result.add_section("Service Overview", "\n".join(service_paragraphs))

            result.add_table(
                "Service Breakdown",
                columns=["Service", "Frequency", "Unit Price"],
                rows=[
                    {
                        "Service": service.get("name", ""),
                        "Frequency": service.get("frequency", ""),
                        "Unit Price": f"{pricing.get('currency', 'USD')} {service.get('price', 0):.2f}",
                    }
                    for service in services
                ],
            )

        if schedule:
            start_date = schedule.get("start_date")
            end_date = schedule.get("end_date")
            notes = schedule.get("notes")
            schedule_lines = []
            if start_date:
                schedule_lines.append(
                    f"Projected start date: {self._format_date(start_date)}"
                )
            if end_date:
                schedule_lines.append(f"Target completion: {self._format_date(end_date)}")
            if notes:
                schedule_lines.append(notes)
            if schedule_lines:
                result.add_section("Schedule", "\n".join(schedule_lines))

        if pricing:
            discount = pricing.get("discount") or 0
            subtotal = sum(float(service.get("price", 0) or 0) for service in services)
            total = subtotal * (1 - discount)
            pricing_lines = [f"Subtotal: {pricing.get('currency', 'USD')} {subtotal:.2f}"]
            if discount:
                pricing_lines.append(f"Discount: {discount * 100:.0f}%")
            pricing_lines.append(f"Total Investment: {pricing.get('currency', 'USD')} {total:.2f}")
            if pricing.get("additional_notes"):
                pricing_lines.append(pricing["additional_notes"])
            result.add_section("Investment Summary", "\n".join(pricing_lines))

        if company:
            contact_lines = [company_name]
            if company.get("representative"):
                contact_lines.append(f"Primary contact: {company['representative']}")
            if company.get("email"):
                contact_lines.append(f"Email: {company['email']}")
            if company.get("phone"):
                contact_lines.append(f"Phone: {company['phone']}")
            result.add_section("Contact Information", "\n".join(contact_lines))

        return result

    def _format_date(self, value: object) -> str:
        if isinstance(value, datetime):
            return value.strftime("%B %d, %Y")
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(value, fmt).strftime("%B %d, %Y")
                except ValueError:
                    continue
            return value
        return str(value)
