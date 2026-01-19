import type { MenuMiddleware } from "@bazza-ui/menu/middleware";
import type {
  Column,
  DataTableFilterActions,
  NumberFilterOperator,
} from "@bazza-ui/filters";
import { SubmenuDef } from "@bazza-ui/dropdown-menu";
import { parseDurationToUnit } from "@/lib/utils";

export function createNumberFilterMiddleware<TData>({
  column,
  actions,
}: {
  column: Column<TData, "number">;
  actions: DataTableFilterActions;
}): MenuMiddleware {
  return {
    transformNodes: (context: any) => {
      const { query, mode, createNode } = context;

      if (mode !== "search" || !query?.trim()) return [];

      // support different units

      const unit = (column as any).meta?.number?.unit as
        | "seconds"
        | "minutes"
        | "hours"
        | undefined;

      // default if missing
      const baseUnit =
        (column.meta?.number?.unit as "seconds" | "minutes" | "hours") ??
        "minutes";

      const parsed = parseDurationToUnit(query, baseUnit);
      if (!parsed) return [];

      const { value, display } = parsed;

      const apply = (operator: NumberFilterOperator) => {
        actions.batch((tx: any) => {
          tx.setFilterValue(column, [value]);
          tx.setFilterOperator(column.id, operator);
        });
      };

      const items: Array<[NumberFilterOperator, string]> = [
        ["is", `is ${display}`],
        ["is not", `is not ${display}`],
        ["is greater than", `is greater than ${display}`],
        [
          "is greater than or equal to",
          `is greater than or equal to ${display}`,
        ],
        ["is less than", `is less than ${display}`],
        ["is less than or equal to", `is less than or equal to ${display}`],
      ];

      return items.map(([op, label]) =>
        createNode({
          kind: "item",
          id: `${column.id}-number-${op}-${query}`,
          label,
          keywords: [query],
          onSelect: () => apply(op),
        })
      );
    },
  };
}

export function createNumberUnitMenu<TData>({
  column,
  actions,
}: {
  column: Column<TData, "number">;
  actions: DataTableFilterActions;
}): SubmenuDef {
  return {
    kind: "submenu",
    id: column.id,
    icon: column.icon,
    label: column.displayName,
    inputPlaceholder: "Enter duration (e.g., 1h, 2 hours, 30mins)...",
    defaults: {
      item: { closeOnSelect: true },
    },
    middleware: createNumberFilterMiddleware({ column, actions }),
  };
}
