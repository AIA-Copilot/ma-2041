/**
 * -------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation.  All Rights Reserved.  Licensed under the MIT License.
 * See License in the project root for license information.
 * -------------------------------------------------------------------------------------------
 */

/**
 * @module LongRunningOperationMiddleware
 */

import { Context } from '@microsoft/microsoft-graph-client';
import { Middleware } from '@microsoft/microsoft-graph-client';

/**
 * @class
 * @implements Middleware
 * Class representing LongRunningOperationMiddleware
 */
export class LongRunningOperationMiddleware implements Middleware {
  /**
   * @private
   * A member representing the location header name
   */
  private static LOCATION_HEADER = 'Location';

  /**
   * @private
   * A member to hold next middleware in the middleware chain
   */
  private nextMiddleware: Middleware;

  /**
   * @private
   * A member to hold the delay in milliseconds
   */
  private delay: number;

  /**
   * @public
   * @constructor
   * Creates an instance of LongRunningOperationMiddleware
   * @param {number} delay - The delay in  milliseconds between each retries for the long-running operation
   */
  public constructor(delay: number, private timeout: number = 600_000) {
    this.delay = delay;
  }

  /**
   * @public
   * @async
   * To execute the current middleware
   * @param {Context} context - The context object of the request
   * @returns A Promise that resolves to nothing
   */
  public async execute(context: Context): Promise<void> {
    if (!context) return;
    const deadline = Date.now() + this.timeout;
    const controller = new AbortController();
    const previousSignal = context.options?.signal;
    const abort = () => controller.abort();
    previousSignal?.addEventListener('abort', abort, { once: true });
    if (previousSignal?.aborted) controller.abort();
    context.options = { ...context.options, signal: controller.signal };
    const timeoutError = () => new Error('Graph connection operation timed out');
    let timer: ReturnType<typeof setTimeout>;
    const expired = new Promise<never>((_, reject) => {
      timer = setTimeout(() => {
        reject(timeoutError());
        controller.abort();
      }, this.timeout);
    });
    const run = async () => {
      let polling = context.request.toString().includes('/operations/');
      while (true) {
        if (Date.now() >= deadline || controller.signal.aborted) throw timeoutError();
        await this.nextMiddleware.execute(context);
        if (Date.now() >= deadline || controller.signal.aborted) throw timeoutError();
        const response = context.response!;
        if (polling) {
          if (!response.ok) throw new Error(`Graph connection operation polling HTTP ${response.status}`);
          const body: any = await response.clone().json();
          // externalConnectors.connectionOperationStatus: completed is the only success.
          // https://learn.microsoft.com/graph/api/resources/externalconnectors-connectionoperation?view=graph-rest-1.0
          if (body?.status === 'completed') return;
          if (body?.status === 'failed') throw new Error('Graph connection operation failed');
          if (body?.status !== 'inprogress') throw new Error('Graph connection operation returned an unknown status');
        } else {
          const location = response.headers.get(LongRunningOperationMiddleware.LOCATION_HEADER);
          if (!location || !location.includes('/operations/')) return;
          if (!response.ok) throw new Error(`Graph connection operation initial HTTP ${response.status}`);
          context.request = location;
          context.options!.method = 'GET';
          context.options!.body = undefined;
          polling = true;
        }
        await new Promise(resolve => setTimeout(resolve, Math.min(this.delay, Math.max(0, deadline - Date.now()))));
      }
    };
    try {
      // Bound transport/body reads too, not just the interval between polls.
      await Promise.race([run(), expired]);
    } finally {
      clearTimeout(timer!);
      previousSignal?.removeEventListener('abort', abort);
    }
  }

  /**
   * @public
   * To set the next middleware in the chain
   * @param {Middleware} next - The middleware instance
   * @returns Nothing
   */
  public setNext(next: Middleware): void {
    this.nextMiddleware = next;
  }
}
